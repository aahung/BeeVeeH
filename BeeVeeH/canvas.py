'''
This class manipulate OpenGL drawing

camera control and perspective control are inspired by https://learnopengl.com/#!Getting-started/Camera
'''

import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
from BeeVeeH.bvh_helper import BVHNode
from BeeVeeH.bvh_render import render

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

class BeeVeeHCanvas(glcanvas.GLCanvas):

    context = None

    def __init__(self, parent_window):
        super().__init__(parent_window, -1)
        self.parent_window = parent_window

        self.init = False
        self.context = glcanvas.GLContext(self)

        self.lastx = self.x = 30
        self.lasty = self.y = 30
        self.size = None

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftMouseUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightMouseDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

        self.bvh_root = None

        # camera control
        self.camera_position = np.array([200.0, 200.0, 200.0])
        self.camera_lookat = [0.0, 0.0, 0.0]
        self.camera_up = [0.0, 1.0, 0.0]
        self.camera_lookat_md = [0.0, 0.0, 0.0] # mouse down
        self.camera_up_md = [0.0, 1.0, 0.0] # mouse down

        # perspective control
        self.fov = 45.0

        # mouse info
        self.last_x = -1;
        self.last_y = -1;
        self.yaw = -135.0
        self.pitch = -45.0

    def OnSize(self, event):
        self.size = self.GetClientSize()
        wx.CallAfter(self.DoSetViewport)
        wx.CallAfter(self.update_perspective)
        event.Skip()

    def DoSetViewport(self):
        if self.size is None:
            self.size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, self.size.width, self.size.height)


    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    def calculate_camera(self):
        front = np.array([np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch)),
                          np.sin(np.radians(self.pitch)),
                          np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))])
        self.camera_front = normalize(front)

    def update_camera(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(self.camera_position[0],
                  self.camera_position[1],
                  self.camera_position[2],
                  self.camera_position[0] + self.camera_front[0],
                  self.camera_position[1] + self.camera_front[1],
                  self.camera_position[2] + self.camera_front[2],
                  self.camera_up[0],
                  self.camera_up[1],
                  self.camera_up[2])

    def update_perspective(self):
        if self.size is None:
            self.size = self.GetClientSize()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.size.width / self.size.height, 10, 800.0);
        glMatrixMode(GL_MODELVIEW) # reset to default

    def InitGL(self):
        # set viewing projection
        glShadeModel(GL_SMOOTH)
        
        self.update_perspective()
        self.calculate_camera()
        self.update_camera()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

    def OnDraw(self):
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        for i in range(-10, 11):
            glBegin(GL_LINES)
            glVertex3f(i * 20, 0, -200);
            glVertex3f(i * 20, 0, 200);
            glEnd()
            glBegin(GL_LINES)
            glVertex3f(-200, 0, i * 20);
            glVertex3f(200, 0, i * 20);
            glEnd()
        
 
        if self.bvh_root:
            render(self.bvh_root)

        if self.size is None:
            self.size = self.GetClientSize()

        self.SwapBuffers()

    def OnLeftMouseDown(self, event):
        self.CaptureMouse()
        self.last_x, self.last_y = event.GetPosition()
        self.mouse_button = 0;

    def OnLeftMouseUp(self, event):
        self.ReleaseMouse()
        self.mouse_button = -1

    def OnRightMouseDown(self, event):
        self.CaptureMouse()
        self.last_x, self.last_y = event.GetPosition()
        self.mouse_button = 1;

    def OnRightMouseUp(self, event):
        self.ReleaseMouse()
        self.mouse_button = -1

    def OnMouseMotion(self, event):
        if event.Dragging() and self.mouse_button >= 0:
            x, y = event.GetPosition()
            offset_x = x - self.last_x
            offset_y = y - self.last_y
            self.last_x, self.last_y = x, y
            if self.mouse_button == 0:
                sensitivity = 0.05
                offset_x *= sensitivity
                offset_y *= sensitivity
                self.yaw   -= offset_x
                self.pitch += offset_y
                if self.pitch > 89.0:
                    self.pitch = 89.0
                if self.pitch < -89.0:
                    self.pitch = -89.0
                self.calculate_camera()
            elif self.mouse_button == 1:
                camera_speed = 0.2
                self.camera_position -= normalize(np.cross(self.camera_front, self.camera_up)) * camera_speed * offset_x
                self.camera_position -= normalize(np.cross(self.camera_front, np.cross(self.camera_front, self.camera_up))) * camera_speed * offset_y
            self.update_camera()

    def OnMouseWheel(self, event):
        sensitivity = 0.1
        self.camera_position -= self.camera_front * event.GetWheelRotation()
        self.update_camera()
            

    def show_bvh_frame(self, bvh_root):
        self.bvh_root = bvh_root
