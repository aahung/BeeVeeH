import wx

class PlaybackPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetBackgroundColour('#ededed')

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.playback_slider = wx.Slider(self, -1, 27, 0, 100,
                style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)


        self.play_button = wx.ToggleButton(self, -1, "Pause", size=(60,-1))
        self.play_button.SetValue(True)

        self.reset_button = wx.Button(self, -1, "Reset", size=(50,-1))

        self.prev_button = wx.Button(self, -1, "<", size=(30,-1))
        self.prev_button.Enable(False)

        self.next_button = wx.Button(self, -1, ">", size=(30,-1))
        self.next_button.Enable(False)


        hbox.AddSpacer(10)
        hbox.Add(self.play_button, 0, wx.ALIGN_CENTER)
        hbox.Add(self.reset_button, 0, wx.ALIGN_CENTER)
        hbox.Add(self.playback_slider, 1, wx.EXPAND)
        hbox.Add(self.prev_button, 0, wx.ALIGN_CENTER)
        hbox.Add(self.next_button, 0, wx.ALIGN_CENTER)
        hbox.AddSpacer(10)

        self.SetSizer(hbox)

    def bind_events(self,
                    OnPlaybackSliderChanged,
                    OnPlayPause,
                    OnResetFrameI,
                    OnPrevFrame,
                    OnNextFrame):
        self.playback_slider.Bind(wx.EVT_SLIDER, OnPlaybackSliderChanged)
        self.play_button.Bind(wx.EVT_TOGGLEBUTTON, OnPlayPause)
        self.reset_button.Bind(wx.EVT_BUTTON, OnResetFrameI)
        self.prev_button.Bind(wx.EVT_BUTTON, OnPrevFrame)
        self.next_button.Bind(wx.EVT_BUTTON, OnNextFrame)

    def set_state(self, is_playing):
        if is_playing:
            self.prev_button.Enable(False)
            self.next_button.Enable(False)
            self.play_button.SetLabel('Pause')
        else:
            self.prev_button.Enable(True)
            self.next_button.Enable(True)
            self.play_button.SetLabel('Play')

    def set_slider_range(self, min, max):
        self.playback_slider.SetRange(min, max)

    def set_slider_value(self, value):
        self.playback_slider.SetValue(value)
