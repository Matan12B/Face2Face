import cv2
import numpy as np
import threading
import time


class VideoDisplay:

    def __init__(self):

        # store latest frame per participant
        self.frames = {}

        # thread safety
        self.lock = threading.Lock()

        self.running = True

        # start display thread
        self.display_thread = threading.Thread(target=self.display_loop)
        self.display_thread.daemon = True
        self.display_thread.start()


    # called by networking code
    def handle_video(self, client_ip, username, img_bytes):

        # decode JPEG bytes
        frame = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        if frame is None:
            return

        # normalize size
        frame = cv2.resize(frame, (320, 240))

        key = f"{username}-{client_ip}"

        with self.lock:
            self.frames[key] = frame


    # remove participant
    def remove_user(self, client_ip, username):

        key = f"{username}-{client_ip}"

        with self.lock:
            if key in self.frames:
                del self.frames[key]


    # build video grid
    def build_grid(self, frames):

        if len(frames) == 0:
            return None

        if len(frames) == 1:
            return frames[0]

        if len(frames) == 2:
            return np.hstack(frames[:2])

        if len(frames) <= 4:

            row1 = np.hstack(frames[:2])
            row2 = np.hstack(frames[2:4])

            return np.vstack((row1, row2))

        # more than 4 users
        row1 = np.hstack(frames[0:3])
        row2 = np.hstack(frames[3:6])

        return np.vstack((row1, row2))


    # display loop
    def display_loop(self):

        while self.running:

            with self.lock:
                frames = list(self.frames.values())

            grid = self.build_grid(frames)

            if grid is not None:
                cv2.imshow("Meeting", grid)

            key = cv2.waitKey(1)

            if key == 27:  # ESC
                self.running = False
                break

            time.sleep(0.01)

        cv2.destroyAllWindows()


# ----------------------------
# Test with webcams
# ----------------------------

def webcam_sender(display, username, camera_id):

    cap = cv2.VideoCapture(camera_id)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # encode frame as jpeg
        success, encoded = cv2.imencode(".jpg", frame)

        if success:
            display.handle_video(
                client_ip=str(camera_id),
                username=username,
                img_bytes=encoded.tobytes()
            )

        time.sleep(0.03)


# ----------------------------
# run test
# ----------------------------

if __name__ == "__main__":

    display = VideoDisplay()

    # simulate two participants
    threading.Thread(
        target=webcam_sender,
        args=(display, "Alice", 0),
        daemon=True
    ).start()

    # if you have second camera
    threading.Thread(
        target=webcam_sender,
        args=(display, "Bob", 1),
        daemon=True
    ).start()

    while display.running:
        time.sleep(1)