import wx
from BeeVeeH.widget_progress_slider_bar import ProgressSliderBar

class PlaybackPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetBackgroundColour('#ededed')

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.playback_slider = ProgressSliderBar(self, -1, 27, 0, 100)

        self.speed_choice = wx.Choice(self, -1, size=(60,-1),
                                      choices=['1/8x', '1/4x', '1/2x', '1x',
                                               '2x', '4x', '8x'])

        self.play_button = wx.ToggleButton(self, -1, "Pause", size=(60,-1))
        self.play_button.SetValue(True)

        self.reset_button = wx.Button(self, -1, "Reset", size=(50,-1))

        self.prev_button = wx.Button(self, -1, "<", size=(30,-1))
        self.prev_button.Enable(False)

        self.next_button = wx.Button(self, -1, ">", size=(30,-1))
        self.next_button.Enable(False)


        hbox.AddSpacer(10)
        hbox.Add(self.play_button, 0, wx.ALIGN_CENTER)
        hbox.AddSpacer(5)
        hbox.Add(self.reset_button, 0, wx.ALIGN_CENTER)
        hbox.AddSpacer(5)
        hbox.Add(self.playback_slider, 1, wx.EXPAND)
        hbox.AddSpacer(5)
        hbox.Add(wx.StaticText(self, -1, 'Speed: '), 0, wx.ALIGN_CENTER)
        hbox.Add(self.speed_choice, 0, wx.ALIGN_CENTER)
        hbox.AddSpacer(5)
        hbox.Add(self.prev_button, 0, wx.ALIGN_CENTER)
        hbox.Add(self.next_button, 0, wx.ALIGN_CENTER)
        hbox.AddSpacer(10)

        self.SetSizer(hbox)

    def set_speed(self, speed):
        string = '%dx' % round(speed)
        if speed < 1:
            string = '1/%dx' % (round(1 / speed),)
        index = self.speed_choice.FindString(string)
        assert(index != wx.NOT_FOUND)
        self.speed_choice.SetSelection(index)

    def get_speed(self):
        index = self.speed_choice.GetSelection()
        string = self.speed_choice.GetString(index).split('x')[0]
        return eval(string)

    def bind_events(self,
                    OnPlaybackSliderChanged,
                    OnPlayPause,
                    OnResetFrameI,
                    OnPrevFrame,
                    OnNextFrame,
                    OnSpeedChosen):
        self.playback_slider.Bind(wx.EVT_SLIDER, OnPlaybackSliderChanged)
        self.play_button.Bind(wx.EVT_TOGGLEBUTTON, OnPlayPause)
        self.reset_button.Bind(wx.EVT_BUTTON, OnResetFrameI)
        self.prev_button.Bind(wx.EVT_BUTTON, OnPrevFrame)
        self.next_button.Bind(wx.EVT_BUTTON, OnNextFrame)
        self.speed_choice.Bind(wx.EVT_CHOICE, OnSpeedChosen)

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

    def GetLoop(self):
        return self.playback_slider.GetLoop()
