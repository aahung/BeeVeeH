import wx

def in_rect(x0, y0, w, h, x, y):
    return x >= x0 and x <= x0 + w and y >= y0 and y <= y0 + h

class ProgressSliderBar(wx.Panel):
    def __init__(self, parent, id, value, start, end):
        wx.Panel.__init__(self, parent, id, size=(-1, 30))
        
        self.parent = parent
        self.font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL, False, 'Courier 10 Pitch')

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

        self.range = None
        self.loop = None
        self.value = None

        self.sliding_knob = 0

        self.has_init = False

    def paint_value_knob(self, dc):
        # draw the value knob
        w, h = self.GetSize()


        x = self.slider_margin + (self.value - self.range[0]) * self.x_per_increment
        self.value_x = x
        self.value_knob_head_x0 = x - self.knob_head_size // 2
        self.value_knob_head_y0 = h // 2 - self.knob_height // 2 - self.knob_head_size

        # draw current value label
        string = '%d' % self.value
        width, height = dc.GetTextExtent(string)
        dc.DrawText(string, x - width // 2, h // 2 + self.slider_height // 2 + self.text_margin)

        dc.SetPen(wx.Pen('#000000'))
        dc.SetBrush(wx.Brush('#000000'))
        dc.DrawRectangle(x - self.knob_width // 2, h // 2 - self.knob_height // 2, self.knob_width, self.knob_height)

        dc.DrawRectangle(self.value_knob_head_x0, self.value_knob_head_y0, 
                              self.knob_head_size, self.knob_head_size)

    def paint_loop_knob(self, dc, i):
        w, h = self.GetSize()

        x = self.slider_margin + (self.loop[i] - self.range[0]) * self.x_per_increment
        if not hasattr(self, 'loop_x'):
            self.loop_x = [0, 0]
            self.loop_knob_head_x0 = [0, 0]
            self.loop_knob_head_y0 = [0, 0]

        self.loop_x[i] = x
        self.loop_knob_head_x0[i] = x + (i - 1) * self.knob_head_size
        if i == 0:
            self.loop_knob_head_x0[i] += 2
        else:
            self.loop_knob_head_x0[i] -= 1
        self.loop_knob_head_y0[i] = h // 2 + self.knob_height // 2

        # draw label
        string = '%d' % self.loop[i]
        width, height = dc.GetTextExtent(string)
        dc.DrawText(string, x - width // 2, h // 2 - self.slider_height // 2 - self.text_margin - height)

        dc.SetPen(wx.Pen('#1D5273'))
        dc.SetBrush(wx.Brush('#1D5273'))
        dc.DrawRectangle(x - self.knob_width // 2, h // 2 - self.knob_height // 2, self.knob_width, self.knob_height)

        dc.DrawRectangle(self.loop_knob_head_x0[i], self.loop_knob_head_y0[i], 
                              self.knob_head_size, self.knob_head_size)

    def OnPaint(self, event):
    
        dc = wx.PaintDC(self)
        dc.SetFont(self.font)
        w, h = self.GetSize()

        if not self.has_init:
            self.slider_height = h / 3
            self.slider_margin = 10
            self.text_margin = 5
            self.knob_height = self.slider_height + 10
            self.knob_width = 3
            self.knob_head_size = 11
            self.has_init = True

        if self.range:
            # draw start and end label
            string = '%d' % self.range[0]
            width, height = dc.GetTextExtent(string)
            dc.DrawText(string, self.slider_margin - self.knob_width - width, h // 2 - height // 2)

            string = '%d' % self.range[1]
            width, height = dc.GetTextExtent(string)
            # update margin, large enough to locate the label
            self.slider_margin = max(self.slider_margin, width + self.knob_width)
            dc.DrawText(string, w - self.slider_margin + self.knob_width, h // 2 - height // 2)

            dc.SetPen(wx.Pen('#000000'))
            dc.SetBrush(wx.Brush('#ffffff'))
            dc.DrawRectangle(self.slider_margin, (h - self.slider_height) // 2, w - 2 * self.slider_margin, self.slider_height)

            self.x_per_increment = ((w - 2 * self.slider_margin) / (self.range[1] - self.range[0]))
            self.paint_value_knob(dc)
            self.paint_loop_knob(dc, 0)
            self.paint_loop_knob(dc, 1)

    def OnSize(self, event):
        self.Refresh()

    def SetRange(self, min, max):
        self.range = [min, max]
        self.loop = [min, max]

    def SetLoop(self, min=None, max=None):
        if min:
            self.loop[0] = min
        if max:
            self.loop[1] = max

    def GetLoop(self):
        return self.loop

    def SetValue(self, value):
        self.value = value
        self.Refresh()

    def GetValue(self):
        return self.value

    def OnLeftMouseDown(self, event):
        self.sliding_knob = 0
        x, y = event.GetPosition()
        if in_rect(self.value_knob_head_x0, self.value_knob_head_y0,
                   self.knob_head_size, self.knob_head_size, x, y):
            self.sliding_knob = 1
            self.last_value_x = self.value_x
        elif in_rect(self.loop_knob_head_x0[0], self.loop_knob_head_y0[0],
                     self.knob_head_size, self.knob_head_size, x, y):
            self.sliding_knob = 2
            self.last_value_x = self.loop_x[0]
        elif in_rect(self.loop_knob_head_x0[1], self.loop_knob_head_y0[1],
                     self.knob_head_size, self.knob_head_size, x, y):
            self.sliding_knob = 3
            self.last_value_x = self.loop_x[1]
        else:
            return
        self.CaptureMouse()
        self.last_x = x

    def OnLeftMouseUp(self, event):
        if self.sliding_knob > 0:
            self.sliding_knob = 0
            self.ReleaseMouse()

    def OnMouseMotion(self, event):
        if self.sliding_knob == 0:
            return
        if event.Dragging() and event.LeftIsDown():
            x, y = event.GetPosition()
            value = (self.last_value_x + x - self.last_x - self.slider_margin) / self.x_per_increment + self.range[0]
            value = round(value)
            if value > self.range[1]:
                value = self.range[1]
            if value < self.range[0]:
                value = self.range[0]
            if self.sliding_knob == 1:
                if self.value != value:
                    self.value = value
                    self.Refresh()
                slider_event = wx.CommandEvent(wx.wxEVT_SLIDER, self.GetId())
                slider_event.SetInt(self.value)
                slider_event.SetEventObject(self)
                self.GetEventHandler().ProcessEvent(slider_event)
            elif self.sliding_knob == 2:
                if value >= self.loop[1]:
                    value = self.loop[1] - 1
                if self.loop[0] != value:
                    self.loop[0] = value
                    self.Refresh()
            elif self.sliding_knob == 3:
                if value <= self.loop[0]:
                    value = self.loop[0] + 1
                if self.loop[1] != value:
                    self.loop[1] = value
                    self.Refresh()

