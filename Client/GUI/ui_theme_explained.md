# `ui_theme.py` — wxPython Explained

A full breakdown of every wxPython concept used in this file.

---

## 📦 Imports

```python
import wx
import wx.adv
```

- **`wx`** — the main wxPython module. Contains everything: windows, controls, drawing, events.
- **`wx.adv`** — the "advanced" sub-module. Contains fancier controls like `HyperlinkCtrl` that aren't in the core.

---

## 🎨 `wx.Colour(R, G, B)`

```python
"primary": wx.Colour(14, 113, 235)
```

Represents a color using Red, Green, Blue values from **0 to 255**.  
Used everywhere to define the `PALETTE` dictionary of named colors for the whole app.

---

## 📐 `wx.Size(width, height)`

```python
wx.Size(min_width, min_height)
wx.Size(-1, 34)   # -1 means "don't care / use default"
```

Represents a 2D size (width × height).  
`-1` is a special value meaning "no constraint on this dimension."  
Used to set minimum sizes for buttons and text inputs.

---

## 🖱️ `wx.Cursor(wx.CURSOR_HAND)`

```python
self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
```

Changes the mouse cursor when hovering over a control.  
`CURSOR_HAND` is the "pointer hand" you see when hovering over links or buttons in a browser.

---

## 🏗️ `wx.Control`

```python
class RoundedButton(wx.Control):
```

The base class for all **interactive** UI elements (buttons, checkboxes, sliders, etc.).  
`RoundedButton` inherits from it instead of `wx.Button` because the built-in button can't have  
rounded corners — so we build a fully custom one and draw 100% of it ourselves.

| Use this when... |
|---|
| You need total visual control over a widget |
| The built-in controls don't look how you want |

---

## 🖼️ `wx.BORDER_NONE`

```python
super().__init__(parent, style=wx.BORDER_NONE, size=size)
```

A **style flag** passed to the control constructor.  
Tells the OS not to draw any system border/frame around this control.  
Without it, you'd see an ugly default border around the custom button.

---

## 🎨 `wx.BG_STYLE_PAINT`

```python
self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
```

Tells wxPython: **"I will draw the background myself in the paint event."**  
This is **required** for flicker-free custom drawing — without it, the OS erases the control  
with a grey rectangle before your paint handler runs, causing visible flicker.

---

## ✏️ Drawing Contexts

These are objects you draw onto. Think of them as a "canvas."

### `wx.ClientDC(window)`

```python
dc = wx.ClientDC(self)
dc.GetTextExtent("Hello")   # → (width, height)
```

A Drawing Context you can use **at any time** (not just during paint).  
Used here only to **measure text size** so `DoGetBestSize` can calculate the correct button dimensions.  
**Never draw visuals with this** — only use it for measurements.

### `wx.AutoBufferedPaintDC(window)`

```python
dc = wx.AutoBufferedPaintDC(self)
```

Used **only inside a `wx.EVT_PAINT` handler**.  
The "AutoBuffered" part means it draws to an offscreen bitmap first, then copies everything  
to the screen at once — this eliminates flickering on repaint.

---

## 🖌️ `wx.Brush(colour)` and `wx.Pen(colour, width)`

```python
dc.SetBackground(wx.Brush(parent_bg))   # fill color
gc.SetPen(wx.Pen(border_colour, 1))     # outline/stroke
```

| Tool | Purpose |
|---|---|
| `wx.Brush` | **Fills** the interior of shapes (like the "fill" bucket in Paint) |
| `wx.Pen` | Draws **outlines/borders** of shapes (like the "pencil" in Paint) |

---

## ✍️ `wx.Font` / `font.PointSize` / `font.SetWeight`

```python
font = control.GetFont()
font.PointSize = max(9, font.PointSize + size_delta)
font.SetWeight(wx.FONTWEIGHT_BOLD)
control.SetFont(font)
```

Every control has a font object attached to it.  
The pattern is always: **get → modify → set back.**

| Property | What it does |
|---|
| `PointSize` | Font size in points (like in Word) |
| `SetWeight(wx.FONTWEIGHT_BOLD)` | Make text bold |
| `SetWeight(wx.FONTWEIGHT_NORMAL)` | Regular weight |

---

## 🖼️ `wx.GraphicsContext` — Modern Anti-Aliased Drawing

This is the **high-quality drawing API** in wxPython. Used for smooth curved shapes.

```python
gc = wx.GraphicsContext.Create(dc)
```

Creates a graphics context wrapping the paint DC. Always check `if gc:` — it can be `None` on some platforms.

### `gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)`

Turns on **smooth edges** (anti-aliasing).  
Without it, curves and diagonal lines look jagged/pixelated.

### `gc.CreatePath()` + `path.AddRoundedRectangle(x, y, w, h, radius)`

```python
path = gc.CreatePath()
path.AddRoundedRectangle(0, 0, width - 1, height - 1, self._radius)
```

A **path** is a shape you build programmatically before drawing it.  
`AddRoundedRectangle` adds a rectangle with rounded corners to that path.  
The `radius` controls how curved the corners are — larger = more pill-shaped.

### `gc.DrawPath(path)`

Renders the path onto the screen using the current pen (border) and brush (fill).

### `gc.GetTextExtent(text)` → `(width, height)`

Measures how wide and tall a piece of text will be when drawn.  
Used to **mathematically center the label** inside the button:

```python
text_w, text_h = gc.GetTextExtent(text)
gc.DrawText(text, (width - text_w) / 2, (height - text_h) / 2)
```

### `gc.SetFont(font, colour)` + `gc.DrawText(text, x, y)`

Sets the font and color for text, then draws it at a given `(x, y)` coordinate.

---

## ⚡ Events & Binding

Events are things that **happen** to a widget. You connect them to handler functions with `Bind`.

```python
self.Bind(wx.EVT_PAINT, self._on_paint)
```
"When a paint event fires on this control, call `self._on_paint`."

| Event | When it fires |
|---|---|
| `wx.EVT_PAINT` | The OS needs the control to redraw itself |
| `wx.EVT_ENTER_WINDOW` | Mouse pointer moves **onto** the control |
| `wx.EVT_LEAVE_WINDOW` | Mouse pointer moves **off** the control |
| `wx.EVT_LEFT_DOWN` | Left mouse button is **pressed** |
| `wx.EVT_LEFT_UP` | Left mouse button is **released** |
| `wx.EVT_SET_FOCUS` | Control gains keyboard focus (e.g. user tabs to it) |
| `wx.EVT_KILL_FOCUS` | Control loses keyboard focus |
| `wx.EVT_BUTTON` | A button was clicked |

### `event.Skip()`

```python
def _on_enter(self, event):
    self._hovered = True
    self.Refresh()
    event.Skip()   # ← important!
```

Tells wxPython: **"I handled this event, but also let the default handler run."**  
Without `.Skip()` on focus/mouse events, the OS-level behavior (like focus rings) breaks.

---

## 🖱️ Mouse Capture

```python
self.CaptureMouse()   # called on LEFT_DOWN
self.ReleaseMouse()   # called on LEFT_UP
self.HasCapture()     # check before releasing
```

**Mouse capture** means: "Even if the mouse moves off this control, keep sending me mouse events."  
This solves the case where a user clicks and drags their mouse off the button before releasing —  
without capture, `LEFT_UP` would never fire for this control.

`HasCapture()` — always check this before calling `ReleaseMouse()` to avoid crashes.

---

## 📣 `wx.CommandEvent` + `wx.PostEvent`

```python
click_evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
click_evt.SetEventObject(self)
wx.PostEvent(self, click_evt)
```

Because `RoundedButton` is not a real `wx.Button`, clicking it won't automatically fire `EVT_BUTTON`.  
So after confirming the mouse was released **inside** the button bounds, we:

1. **Create** a fake `EVT_BUTTON` event manually
2. **Stamp it** with our widget's ID and reference (`SetEventObject`)
3. **Post it** to the event queue with `wx.PostEvent` — so any external code that did `Bind(EVT_BUTTON, ...)` on this button will fire normally

---

## 🔁 `DoGetBestSize()`

```python
def DoGetBestSize(self):
    ...
    return wx.Size(width, height)
```

A special method wxPython calls to ask: **"What is your ideal/minimum size?"**  
Override it on custom controls so that layout managers (sizers) can auto-size them correctly.

---

## 🔧 `SetMinSize` / `SetInitialSize`

```python
button.SetMinSize(wx.Size(min_width, min_height))
button.SetInitialSize(wx.Size(min_width, min_height))
```

- `SetMinSize` — the control will never be shrunk below this size by a sizer.
- `SetInitialSize` — hints to the layout system what the starting size should be.

---

## 🔗 `wx.adv.HyperlinkCtrl`

```python
link = wx.adv.HyperlinkCtrl(parent, label=label, url="")
link.SetNormalColour(...)
link.SetHoverColour(...)
link.SetVisitedColour(...)
```

A built-in wx control that **looks and behaves like a clickable hyperlink**.  
Has three visual states with separate colors:

| State | When |
|---|---|
| Normal | Default, unvisited |
| Hover | Mouse is over it |
| Visited | User has clicked it before |

`url=""` — set to empty string since we handle the click event ourselves (not opening a browser).

---

## 🔄 The Custom Drawing Pattern (Summary)

The entire `RoundedButton` follows this standard wxPython pattern for custom widgets:

```
1. Inherit from wx.Control
2. Set BG_STYLE_PAINT (prevent flicker)
3. Bind EVT_PAINT → draw EVERYTHING yourself
4. Track state with flags (_hovered, _pressed)
5. On state change → call self.Refresh() to trigger repaint
6. In _on_paint → choose colors based on state → draw shape + text
```

This pattern applies to any custom widget you'll ever build in wxPython.

