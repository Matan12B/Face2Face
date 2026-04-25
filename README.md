# 🎥 Python Zoom

A video-conferencing app built from scratch in Python — no third-party meeting SDKs.

## ✨ Features

- 🔐 **Encrypted** — Diffie-Hellman key exchange + AES-CBC for all traffic
- 📹 **Live video & audio** — OpenCV + sounddevice, streamed over UDP
- 🔇 **Mute / camera controls** — state synced instantly to all participants
- 👤 **User accounts** — sign-up & login with an SQLite database
- 🏠 **Host & guest roles** — host creates a meeting, guests join with a 5-letter code
- 🖥️ **Native GUI** — wxPython dark theme with per-participant video panels

## 🚀 Setup

**Requirements:** Python 3.10+

```bash
pip install -r requirements.txt
```

Edit `Common/settings.txt` to point at your server:

```ini
server_ip=127.0.0.1
server_port=2000
video_port=5000
audio_port=3000
dh_p=797
dh_g=100
```

**Run the server:**
```bash
python -m Server.serverLogic
```

**Run the client** (on each machine):
```bash
python -m Client.GUI.main_app
```

## 🎮 Usage

1. Sign up or log in
2. **Create** a meeting → get a 5-letter code → share it
3. Others **Join** with the code
4. In the call: toggle mic 🎙️, camera 📹, or leave 🚪
   - Everyone starts **muted** with **camera off**
   - Host leaving ends the meeting for everyone

## 🏗️ How It Works

```
Central Server (TCP)          — auth, meeting create/join
    │
    ├── Host (Client)
    │       │◄── TCP control (mute/camera/join events)
    │       │◄── UDP video + audio
    └── Guest (Client)
```

| Channel | Transport | Used for |
|---|---|---|
| Signalling | TCP → Server | Login, meeting management |
| Control | TCP → Host | Mute, camera, join/leave |
| Video | UDP | JPEG frames @ 15 fps |
| Audio | UDP | 16-bit PCM @ 16 kHz |



