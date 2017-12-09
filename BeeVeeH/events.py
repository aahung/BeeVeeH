import wx

'''
FRAME_NUMBER_UPDATE event
'''
EVT_FRAME_NUMBER_UPDATE_ID = wx.NewEventType()
EVT_FRAME_NUMBER_UPDATE = wx.PyEventBinder(EVT_FRAME_NUMBER_UPDATE_ID, 1)
class FrameNumberUpdateEvent(wx.PyEvent):
    def __init__(self, frame_number):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_FRAME_NUMBER_UPDATE_ID)
        self.frame_number = frame_number

'''
FRAME_NUMBER_UPDATE event
'''
EVT_FRAME_UPDATE_ID = wx.NewEventType()
EVT_FRAME_UPDATE = wx.PyEventBinder(EVT_FRAME_UPDATE_ID, 1)
class FrameUpdateEvent(wx.PyEvent):
    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_FRAME_UPDATE_ID)