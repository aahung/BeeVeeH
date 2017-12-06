import wx
from wx import glcanvas
from OpenGL.GL import *

class BeeVeeHCanvas(glcanvas.GLCanvas):

    context = None

    def __init__(self, parent_window):
        attribList = (glcanvas.WX_GL_RGBA, # RGBA
                      glcanvas.WX_GL_DOUBLEBUFFER, # Double Buffered
                      glcanvas.WX_GL_DEPTH_SIZE, 24) # 24 bit
        super().__init__(parent_window, -1, attribList=attribList)
        self.parent_window = parent_window

        self.Bind(wx.EVT_PAINT, self.OnDraw)
        self.Bind(wx.EVT_SIZE, self.OnReshape)
        
        self.GLinitialized = False

    def refreshContext(self):
        if not self.context:
            self.context = glcanvas.GLContext(self)
        self.SetCurrent(self.context)

    def OnInitGLIfNot(self):
        if self.GLinitialized:
            return
        self.GLinitialized = True
        glClearColor(1, 1, 1, 1)

    def OnReshape(self, event):
        try:
            width, height = event.GetSize()
        except:
            width = event.GetSize().width
            height = event.GetSize().height

        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-0.5, 0.5, -0.5, 0.5, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.Refresh()
        self.Update()

     
    def OnDraw(self, event):
        self.refreshContext()
        
        self.OnInitGLIfNot();

        glClear(GL_COLOR_BUFFER_BIT)

        glBegin(GL_TRIANGLES)
        glColor(0, 0, 0)
        glVertex(-.25, -.25)
        glVertex(.25, -.25)
        glVertex(0, .25)
        glEnd()

        self.SwapBuffers()

    def show_bvh_frame(self, bvh_frame):
        pass