import wx
from .home_frame import HomeFrame


class ZoomApp(wx.App):

    def OnInit(self):
        frame = HomeFrame()
        frame.Show()
        return True


if __name__ == "__main__":
    app = ZoomApp()
    app.MainLoop()