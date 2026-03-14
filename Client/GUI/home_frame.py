import wx
from .lobby_frame import LobbyFrame
from .call_frame import CallFrame


class HomeFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title="Python Zoom", size=(400,300))

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(panel, label="Python Zoom")
        font = title.GetFont()
        font.PointSize += 10
        title.SetFont(font)

        self.start_btn = wx.Button(panel, label="Start Meeting")
        self.join_btn = wx.Button(panel, label="Join Meeting")
        self.code_box = wx.TextCtrl(panel, hint="Meeting Code")

        vbox.Add(title, 0, wx.ALL | wx.CENTER, 20)
        vbox.Add(self.start_btn, 0, wx.ALL | wx.EXPAND, 10)
        vbox.Add(self.code_box, 0, wx.ALL | wx.EXPAND, 10)
        vbox.Add(self.join_btn, 0, wx.ALL | wx.EXPAND, 10)

        panel.SetSizer(vbox)

        self.start_btn.Bind(wx.EVT_BUTTON, self.start_meeting)
        self.join_btn.Bind(wx.EVT_BUTTON, self.join_meeting)


    def start_meeting(self, event):
        lobby = LobbyFrame(host=True)
        lobby.Show()
        self.Close()


    def join_meeting(self, event):

        code = self.code_box.GetValue()

        if not code:
            wx.MessageBox("Enter meeting code")
            return

        call = CallFrame()
        call.Show()
        self.Close()