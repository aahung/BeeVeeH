#!/usr/bin/env python3

import sys
sys.path = ['lib'] + sys.path

import _thread
import sched
import time
import wx
from Canvas import BeeVeeHCanvas
import BVH
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

        self.initCanvas()


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

    def initCanvas(self):
        print('init canvas')
        
        self.canvas = BeeVeeHCanvas(self)
        print('setting canvas size to %s' % str(self.GetSize()))
        self.canvas.SetSize(self.GetSize())

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.processEraseBackgroundEvent)
        self.Bind(wx.EVT_SIZE, self.processSizeEvent)


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

    #
    # wxPython Window Handlers
    def processEraseBackgroundEvent(self, event):
        """Process the erase background event."""
        pass # Do nothing, to avoid flashing on MSWin

    def processSizeEvent(self, event):
        """Process the resize event."""
        if self.canvas is not None:
            # Make sure the frame is shown before calling SetCurrent.
            size = self.GetGLExtents()
            self.canvas.SetSize(size)

            self.canvas.Show()

        event.Skip()

    def timer_show_frame(self):
        print('showing frame %d' % self.frame_i)
        BVH.render_frame(self.root, self.frames[self.frame_i][:]) # [:] is mandatory here
        self.canvas.show_bvh_frame(self.root)
        self.frame_i = (self.frame_i + 1) % len(self.frames)
        self.canvas.Refresh(False)

    def show_frame(self):
        self.root, self.frames = BVH.load('test/bvh_files/0005_2FeetJump001.bvh')
        self.frame_i = 0;
        periodic_scheduler = PeriodicScheduler()  
        periodic_scheduler.setup(0.01, self.timer_show_frame) # it executes the event just once  
        periodic_scheduler.run() # it starts the scheduler  

        

if __name__ == '__main__':
    app = wx.App()
    frm = AppFrame(None, title='BeeVeeH')
    frm.Show()
    _thread.start_new_thread(frm.show_frame, ())
    app.MainLoop()