import wx
import wx.adv


PALETTE = {
    "app_bg": wx.Colour(244, 247, 251),
    "surface": wx.Colour(255, 255, 255),
    "surface_alt": wx.Colour(233, 240, 250),
    "surface_muted": wx.Colour(247, 249, 252),
    "border": wx.Colour(220, 228, 240),
    "primary": wx.Colour(14, 113, 235),
    "primary_dark": wx.Colour(10, 86, 190),
    "sidebar": wx.Colour(11, 26, 48),
    "text": wx.Colour(20, 33, 61),
    "text_muted": wx.Colour(98, 112, 136),
    "text_inverted": wx.Colour(255, 255, 255),
    "success_bg": wx.Colour(231, 248, 238),
    "success_text": wx.Colour(25, 110, 67),
    "warning_bg": wx.Colour(255, 244, 224),
    "warning_text": wx.Colour(153, 88, 13),
    "danger": wx.Colour(218, 61, 48),
    "danger_dark": wx.Colour(177, 40, 35),
    "danger_bg": wx.Colour(255, 234, 231),
    "danger_text": wx.Colour(155, 34, 28),
    "call_bg": wx.Colour(0, 0, 0),
    "call_surface": wx.Colour(12, 12, 14),
    "call_surface_alt": wx.Colour(22, 22, 26),
    "video_tile": wx.Colour(14, 14, 17),
    "call_ctrl": wx.Colour(38, 40, 50),
    "call_ctrl_text": wx.Colour(210, 215, 228),
    "call_ctrl_active": wx.Colour(180, 35, 35),
    "call_ctrl_danger": wx.Colour(160, 30, 30),
}


def style_window(window, bg, fg=None):
    window.SetBackgroundColour(bg)
    if fg is not None:
        window.SetForegroundColour(fg)
    return window


def style_text(control, colour=None, size_delta=0, bold=False):
    font = control.GetFont()
    font.PointSize = max(9, font.PointSize + size_delta)
    font.SetWeight(wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL)
    control.SetFont(font)
    if colour is not None:
        control.SetForegroundColour(colour)
    return control


def style_text_input(control, hint=""):
    control.SetMinSize(wx.Size(-1, 34))
    control.SetBackgroundColour(PALETTE["surface_muted"])
    control.SetForegroundColour(PALETTE["text"])
    style_text(control, PALETTE["text"], size_delta=5)
    if hint:
        control.SetHint(hint)
    return control


def create_button(parent, label, kind="primary", min_height=44, min_width=-1):
    button = wx.Button(parent, label=label)
    return style_button(button, kind=kind, min_height=min_height, min_width=min_width)


def style_button(button, kind="primary", min_height=44, min_width=-1):
    palettes = {
        "primary": (PALETTE["primary"], PALETTE["text_inverted"]),
        "secondary": (PALETTE["surface_alt"], PALETTE["text"]),
        "ghost": (PALETTE["surface_muted"], PALETTE["text"]),
        "warning": (PALETTE["warning_bg"], PALETTE["warning_text"]),
        "danger": (PALETTE["danger"], PALETTE["text_inverted"]),
        "danger_soft": (PALETTE["danger_bg"], PALETTE["danger_text"]),
        "call": (PALETTE["call_ctrl"], PALETTE["call_ctrl_text"]),
        "call_active": (PALETTE["call_ctrl_active"], PALETTE["text_inverted"]),
        "call_danger": (PALETTE["call_ctrl_danger"], PALETTE["text_inverted"]),
    }

    bg, fg = palettes.get(kind, palettes["primary"])

    button.SetMinSize(wx.Size(min_width, min_height))
    if hasattr(button, "SetInitialSize"):
        button.SetInitialSize(wx.Size(min_width, min_height))

    button.SetBackgroundColour(bg)
    button.SetForegroundColour(fg)
    style_text(button, fg, bold=True)

    font = button.GetFont()
    font.SetWeight(wx.FONTWEIGHT_BOLD)
    button.SetFont(font)

    return button


def create_link(parent, label):
    link = wx.adv.HyperlinkCtrl(parent, label=label, url="")
    link.SetNormalColour(PALETTE["primary"])
    link.SetHoverColour(PALETTE["primary_dark"])
    link.SetVisitedColour(PALETTE["primary"])
    style_text(link, PALETTE["primary"], bold=True)
    return link


def style_status_panel(panel, label, tone="neutral"):
    tones = {
        "neutral": (PALETTE["surface_alt"], PALETTE["text_muted"]),
        "success": (PALETTE["success_bg"], PALETTE["success_text"]),
        "error": (PALETTE["danger_bg"], PALETTE["danger_text"]),
        "warning": (PALETTE["warning_bg"], PALETTE["warning_text"]),
    }
    bg, fg = tones.get(tone, tones["neutral"])
    style_window(panel, bg)
    style_window(label, bg, fg)
    style_text(label, fg)