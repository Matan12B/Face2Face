import wx
import cv2
import numpy as np


class FakeCamera:
    """Temporary camera generator for testing UI"""

    def __init__(self, name):
        self.name = name

    def get_frame(self):

        frame = np.zeros((240,320,3), dtype=np.uint8)

        cv2.putText(
            frame,
            self.name,
            (50,120),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

        return frame


class CallFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title="Meeting", size=(900,700))

        panel = wx.Panel(self)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # -----------------
        # Video grid
        # -----------------

        self.video_grid = wx.GridSizer(2,2,5,5)
        self.video_panels = []

        for i in range(4):

            bitmap = wx.StaticBitmap(panel)
            bitmap.SetMinSize((320,240))

            self.video_panels.append(bitmap)
            self.video_grid.Add(bitmap,1,wx.EXPAND)

        main_sizer.Add(self.video_grid,1,wx.EXPAND | wx.ALL,10)

        # -----------------
        # Control bar
        # -----------------

        controls = wx.BoxSizer(wx.HORIZONTAL)

        self.mic_btn = wx.Button(panel,label="Mute")
        self.cam_btn = wx.Button(panel,label="Camera Off")
        self.leave_btn = wx.Button(panel,label="Leave")

        controls.Add(self.mic_btn,0,wx.ALL,5)
        controls.Add(self.cam_btn,0,wx.ALL,5)
        controls.AddStretchSpacer()
        controls.Add(self.leave_btn,0,wx.ALL,5)

        main_sizer.Add(controls,0,wx.EXPAND | wx.ALL,10)

        panel.SetSizer(main_sizer)

        # Events
        self.leave_btn.Bind(wx.EVT_BUTTON,self.leave_call)

        # Fake cameras for testing
        self.cameras = [
            FakeCamera("Alice"),
            FakeCamera("Bob"),
            FakeCamera("Charlie"),
            FakeCamera("You")
        ]

        # Timer updates video
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.update_frames)
        self.timer.Start(30)


    def update_frames(self,event):

        for i,cam in enumerate(self.cameras):

            frame = cam.get_frame()

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h,w = rgb.shape[:2]

            bitmap = wx.Bitmap.FromBuffer(w,h,rgb)

            self.video_panels[i].SetBitmap(bitmap)


    def leave_call(self,event):
        self.timer.Stop()
        self.Close()