import _thread
import copy
from threading import Thread
import sched
import time
import os
import wx
from BeeVeeH.canvas import BeeVeeHCanvas
import BeeVeeH.bvh_helper as BVH
from BeeVeeH.panel_playback import PlaybackPanel
from BeeVeeH.panel_styling import StylingPanel
from BeeVeeH.events import *

class PeriodicScheduler(object):
    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.interval = None
        self.stop = False

    def setup(self, interval, action, actionargs=()):
        if self.stop:
            return
        if not self.interval:
            self.interval = interval
        action(*actionargs)
        self.scheduler.enter(self.interval, 1, self.setup,
                            (self.interval, action, actionargs))

    def set_interval(self, interval):
        self.interval = interval

    def run(self):
        self.scheduler.run()

class AppFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(AppFrame, self).__init__(*args, **kw)

        self.makeMenuBar()

        self.CreateStatusBar()

        self.SetStatusText("Welcome to BeeVeeH! Command/Ctrl-O to open a file.")

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.canvas = BeeVeeHCanvas(panel)
        self.canvas.SetSize(panel.GetSize())
        
        vbox.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 0)

        self.playback_panel = PlaybackPanel(panel, size=(-1, 55))
        self.styling_panel = StylingPanel(panel, size=(-1, 55))
        self.playback_panel.set_speed(1)
        self.playback_panel.bind_events(self.OnPlaybackSliderChanged,
                                        self.OnPlayPause,
                                        self.OnResetFrameI,
                                        self.OnPrevFrame,
                                        self.OnNextFrame,
                                        self.OnSpeedChosen)
        self.styling_panel.bind_events(self.OnConnectorThinknessChanged,
                                       self.OnJointRadiusChanged,
                                       self.OnHeadJointDoubleSizeChanged,
                                       self.OnSculptureModeChanged,
                                       self.OnSculptureIntervalChanged)
        

        self.Bind(EVT_FRAME_NUMBER_UPDATE, self.OnFrameNumberUpdate)
        self.Bind(EVT_FRAME_UPDATE, self.OnFrameUpdate)
        self.Bind(EVT_NEED_REFRESH, self.ForceRefresh)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        vbox.Add(self.playback_panel, 0, wx.EXPAND | wx.ALL, 0)
        vbox.Add(self.styling_panel, 0, wx.EXPAND | wx.ALL, 0)

        panel.SetSizer(vbox)
        panel.Layout()

        # Fix widget "flickering" on Windows
        self.SetDoubleBuffered(True)

        self.Centre()
        self.Show()

        self.frame_time = 0.1
        self.is_playing = False
        self.frames = None
        self.sculpture_mode = False
        self.worker_thread = WorkerThread(self)

    def makeMenuBar(self):
        fileMenu = wx.Menu()
        openItem = fileMenu.Append(-1, "&Open...\tCtrl-O",
                                    "Open BVH format file")
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnMenuOpen, openItem)
        self.Bind(wx.EVT_MENU, self.OnMenuExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnMenuAbout, aboutItem)

    def OnMenuExit(self, event):
        self.Close(True)

    def OnMenuOpen(self, event):
        self.pause()
        with wx.FileDialog(self, "Open BVH file", wildcard="BVH files (*.bvh)|*.bvh",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            file_path = fileDialog.GetPath()
            try:
                print('opening %s' % file_path)
                self.play_file(file_path, None)
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)
        self.play()


    def OnMenuAbout(self, event):
        wx.MessageBox("A Python based BVH player",
                      "BeeVeeH",
                      wx.OK|wx.ICON_INFORMATION)

    def ForceRefresh(self, event):
        self.SetSize(self.GetSize())
        self.Refresh()
        self.Update()

    def GetGLExtents(self):
        return self.GetClientSize()

    def OnClose(self, event):
        self.worker_thread.stop()
        event.Skip()

    def OnFrameNumberUpdate(self, event):
        # this update makes animation not smooth
        self.playback_panel.set_slider_value(event.frame_number)
        if event.frame_number == len(self.frames) and self.is_test_run:
            self.Close()

    def OnFrameUpdate(self, event):
        clean = event.frame_number == self.playback_panel.GetLoop()[0] or not self.sculpture_mode
        self.canvas.show_bvh_frame(self.root, clean=clean)
        self.canvas.Refresh()

    def play_file(self, file_path, test):
        '''
        If test is true, after finish the playback, quit the application
        '''
        self.is_test_run = test
        self.SetStatusText('Showing %s. Mouse left button to rotate, '
                           'mouse right button to move, '
                           'mouse wheel to zoom' % os.path.basename(file_path))
        self.root, self.frames, self.frame_time = BVH.load(file_path)
        if self.is_test_run:
            self.frames = self.frames[:100]
        self.frame_i = 0;
        self.playback_panel.set_slider_range(1, len(self.frames))
        self.worker_thread.set_interval(self.frame_time)

    def play(self):
        self.is_playing = True
        self.playback_panel.set_state(True)

    def pause(self):
        self.is_playing = False
        self.playback_panel.set_state(False)

    def OnPlayPause(self, event):
        if event.IsChecked():
            self.play()
        else:
            self.pause()

    def OnPlaybackSliderChanged(self, event):
        if self.is_playing == True:
            return
        self.frame_i = event.GetEventObject().GetValue() - 1

    def OnResetFrameI(self, event):
        self.frame_i = 0
        wx.PostEvent(self, FrameNumberUpdateEvent(1))

    def OnNextFrame(self, event):
        self.frame_i = self.frame_i + 1
        if self.frame_i > min(len(self.frames) - 1, self.playback_panel.GetLoop()[1] - 1):
            self.frame_i = min(len(self.frames) - 1, self.playback_panel.GetLoop()[1] - 1)

    def OnPrevFrame(self, event):
        self.frame_i = (self.frame_i - 1)
        if self.frame_i < max(0, self.playback_panel.GetLoop()[0] - 1):
            self.frame_i = max(0, self.playback_panel.GetLoop()[0] - 1)

    def OnConnectorThinknessChanged(self, event):
        self.canvas.RENDER_CONFIG.CONNECTOR_RADIUS = event.GetEventObject().GetValue() / 2

    def OnJointRadiusChanged(self, event):
        self.canvas.RENDER_CONFIG.JOINT_RADIUS = event.GetEventObject().GetValue()

    def OnHeadJointDoubleSizeChanged(self, event):
        self.canvas.RENDER_CONFIG.HEAD_JOINT_DOUBLE_SIZE = event.IsChecked()

    def OnSculptureModeChanged(self, event):
        self.sculpture_mode = event.IsChecked()

    def OnSculptureIntervalChanged(self, event):
        try:
            self.canvas.SculptureInterval = int(event.GetString())
        except Exception as e:
            # user hasn't finished typing yet
            pass

    def OnSpeedChosen(self, event):
        self.speed = self.playback_panel.get_speed()
        self.worker_thread.set_interval(self.frame_time / self.speed)

class WorkerThread(Thread):
    def __init__(self, notify_window):
        Thread.__init__(self)
        self._notify_window = notify_window
        self.did_force_refresh_frame = False
        self.start()

    def loop(self):
        if not self.did_force_refresh_frame:
            wx.PostEvent(self._notify_window, NeedFreshEvent())
            self.did_force_refresh_frame = True

        notify_window = self._notify_window
        if not notify_window.frames:
            return
        if notify_window.sculpture_mode and notify_window.is_playing:
            notify_window.root = copy.deepcopy(notify_window.root)
        notify_window.root.load_frame(notify_window.frames[notify_window.frame_i][:]) # [:] is mandatory here
        frame_number = notify_window.frame_i + 1
        wx.PostEvent(self._notify_window, FrameNumberUpdateEvent(frame_number))
        wx.PostEvent(self._notify_window, FrameUpdateEvent(frame_number))
        if notify_window.is_playing == False:
            return
        notify_window.frame_i = (notify_window.frame_i + 1) % len(notify_window.frames)
        if notify_window.frame_i > notify_window.playback_panel.GetLoop()[1] - 1:
            notify_window.frame_i = notify_window.playback_panel.GetLoop()[0] - 1
        if notify_window.frame_i < notify_window.playback_panel.GetLoop()[0] - 1:
            notify_window.frame_i = notify_window.playback_panel.GetLoop()[0] - 1

    def run(self):
        notify_window = self._notify_window
        notify_window.play()
        self.periodic_scheduler = PeriodicScheduler()  
        self.periodic_scheduler.setup(notify_window.frame_time, self.loop)
        self.periodic_scheduler.run()

    def set_interval(self, interval):
        self.periodic_scheduler.set_interval(interval)

    def stop(self):
        self.periodic_scheduler.stop = True

def start(file_path=None, test=False):
    try:
        app = wx.App()
    except SystemExit as e:
        # no display
        print(e)
        return False
    frame = AppFrame(None, title='BeeVeeH', size=(1000, 800))
    if file_path:
        frame.play_file(file_path, test)
    app.MainLoop()
    return True
