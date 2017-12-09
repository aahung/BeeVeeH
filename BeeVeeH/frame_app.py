import _thread
from threading import Thread
import sched
import time
import wx
from BeeVeeH.canvas import BeeVeeHCanvas
import BeeVeeH.bvh_helper as BVH
from BeeVeeH.panel_playback import PlaybackPanel
from BeeVeeH.events import *

class PeriodicScheduler(object):                                                  
    def __init__(self):                                                           
        self.scheduler = sched.scheduler(time.time, time.sleep)                   
                                                                            
    def setup(self, interval, action, actionargs=()):                             
        action(*actionargs)                                                       
        self.scheduler.enter(interval, 1, self.setup,                             
                        (interval, action, actionargs))                           
                                                                        
    def run(self):                                                                
        self.scheduler.run()

class AppFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(AppFrame, self).__init__(*args, **kw)

        self.makeMenuBar()

        self.CreateStatusBar()

        self.SetStatusText("Welcome to BeeVeeH!")

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.canvas = BeeVeeHCanvas(panel)
        self.canvas.SetSize(panel.GetSize())
        
        vbox.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 0)

        playback_panel = wx.Panel(panel, size=(-1, 50))
        playback_panel.SetBackgroundColour('#ededed')
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.playback_slider = wx.Slider(playback_panel, -1, 27, 0, 100,
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
        hbox.AddSpacer(10)
        self.play_button = wx.ToggleButton(playback_panel, -1, "pause", size=(60,-1))
        self.play_button.SetValue(True)
        self.play_button.Bind(wx.EVT_TOGGLEBUTTON, self.play_pause)
        hbox.Add(self.play_button, 0, wx.ALIGN_CENTER)
        self.reset_button = wx.Button(playback_panel, -1, "reset", size=(50,-1))
        hbox.Add(self.reset_button, 0, wx.ALIGN_CENTER)
        hbox.Add(self.playback_slider, 1, wx.EXPAND)
        self.prev_button = wx.Button(playback_panel, -1, "<", size=(30,-1))
        self.prev_button.Enable(False)
        self.next_button = wx.Button(playback_panel, -1, ">", size=(30,-1))
        self.next_button.Enable(False)
        hbox.Add(self.prev_button, 0, wx.ALIGN_CENTER)
        hbox.Add(self.next_button, 0, wx.ALIGN_CENTER)
        hbox.AddSpacer(10)
        playback_panel.SetSizer(hbox)

        self.Bind(EVT_FRAME_NUMBER_UPDATE, self.OnFrameNumberUpdate)
        self.Bind(EVT_FRAME_UPDATE, self.OnFrameUpdate)

        vbox.Add(playback_panel, 0, wx.EXPAND | wx.ALL, 0)

        panel.SetSizer(vbox)

        self.Centre()
        self.Show()

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
        with wx.FileDialog(self, "Open BVH file", wildcard="BVH files (*.bvh)|*.bvh",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            try:
                print('opening %s' % pathname)
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)


    def OnMenuAbout(self, event):
        wx.MessageBox("A Python based BVH player",
                      "BeeVeeH",
                      wx.OK|wx.ICON_INFORMATION)

    def GetGLExtents(self):
        return self.GetClientSize()

    def OnFrameNumberUpdate(self, event):
        # this update makes animation not smooth
        self.playback_slider.SetValue(event.frame_number)
        if event.frame_number == len(self.frames) and self.is_test_run:
            self.Close()

    def OnFrameUpdate(self, event):
        self.canvas.show_bvh_frame(self.root)
        self.canvas.Refresh()

    def play_file(self, file_path, test):
        '''
        If test is true, after finish the playback, quit the application
        '''
        self.is_test_run = test
        self.SetStatusText('Showing %s' % file_path)
        self.root, self.frames, self.frame_time = BVH.load(file_path)
        self.frame_i = 0;
        self.playback_slider.SetRange(1, len(self.frames))
        WorkerThread(self)

    def play_pause(self, event):
        if event.IsChecked():
            self.play_button.SetLabel('pause')
        else:
            self.play_button.SetLabel('play')

class WorkerThread(Thread):
    def __init__(self, notify_window):
        Thread.__init__(self)
        self._notify_window = notify_window
        self.start()

    def loop(self):
        notify_window = self._notify_window
        if notify_window.play_button.GetValue() == False:
            return
        BVH.render_frame(notify_window.root, notify_window.frames[notify_window.frame_i][:]) # [:] is mandatory here
        frame_number = notify_window.frame_i + 1
        notify_window.frame_i = (notify_window.frame_i + 1) % len(notify_window.frames)
        wx.PostEvent(self._notify_window, FrameNumberUpdateEvent(frame_number))
        wx.PostEvent(self._notify_window, FrameUpdateEvent())

    def run(self):
        notify_window = self._notify_window
        periodic_scheduler = PeriodicScheduler()  
        periodic_scheduler.setup(notify_window.frame_time, self.loop)
        periodic_scheduler.run()

def start(file_path, test=False):
    app = wx.App()
    frm = AppFrame(None, title='BeeVeeH')
    frm.Show()
    _thread.start_new_thread(frm.play_file, (file_path, test))
    app.MainLoop()
