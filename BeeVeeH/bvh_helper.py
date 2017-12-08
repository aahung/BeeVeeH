from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import bvh as BVHLIB

class BVHChannel(object):
    FunctionMap = {
        'Xposition': lambda x: glTranslatef(x, 0.0, 0.0),
        'Yposition': lambda x: glTranslatef(0.0, x, 0.0),
        'Zposition': lambda x: glTranslatef(0.0, 0.0, x),
        'Xrotation': lambda x: glRotatef(x, 1.0, 0.0, 0.0),
        'Yrotation': lambda x: glRotatef(x, 0.0, 1.0, 0.0),
        'Zrotation': lambda x: glRotatef(x, 0.0, 0.0, 1.0)
    }
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.value = 0.0

    def set_value(self, value):
        self.value = value

    def execute(self):
        BVHChannel.FunctionMap[self.name](self.value)

    def str(self):
        return 'Channel({name}) = {value}'.format(name=self.name, value=self.value)

class BVHNode(object):
    def __init__(self, name, offsets, channel_names, children):
        super().__init__()
        self.name = name
        self.children = children # []
        self.channels = [BVHChannel(cn) for cn in channel_names] # []
        self.offsets = offsets # x, y, z

    def paint_connector(self):
        '''This function is inspired by 
        http://lifeofaprogrammergeek.blogspot.ca/2008/07/rendering-cylinder-between-two-points.html
        '''
        quadric=gluNewQuadric()
        subdivisions = 10
        radius = 1

        x1 = 0
        y1 = 0
        z1 = 0
        x2 = -self.offsets[0]
        y2 = -self.offsets[1]
        z2 = -self.offsets[2]

        vx = x2-x1
        vy = y2-y1
        vz = z2-z1

        # handle the degenerate case of z1 == z2 with an approximation
        if vz == 0:
            vz = .0001;

        v = math.sqrt(vx * vx + vy * vy + vz * vz)
        ax = 57.2957795 * math.acos( vz/v )
        if  vz < 0.0:
            ax = -ax
        rx = -vy * vz
        ry = vx * vz

        glPushMatrix()

        # draw the cylinder body
        glTranslatef( x1,y1,z1 )
        glRotatef(ax, rx, ry, 0.0)
        gluQuadricOrientation(quadric, GLU_OUTSIDE)
        gluCylinder(quadric, radius, radius, v, subdivisions, 1)

        # draw the first cap
        gluQuadricOrientation(quadric,GLU_INSIDE);
        gluDisk( quadric, 0.0, radius, subdivisions, 1);
        glTranslatef( 0,0,v );

        # draw the second cap
        gluQuadricOrientation(quadric,GLU_OUTSIDE);
        gluDisk( quadric, 0.0, radius, subdivisions, 1);

        glPopMatrix();

    def paint_end(self):
        glutSolidSphere(1, 20, 20);

    def paint(self):
        # self.paint_connector()
        glPushMatrix()
        glTranslatef(self.offsets[0],
                     self.offsets[1],
                     self.offsets[2]);
        
        self.paint_end()
        self.paint_connector()

        glPushMatrix()

        for channel in self.channels:
            channel.execute()
        
        for child in self.children:
            child.paint()

        glPopMatrix()
        glPopMatrix()

    def str(self):
        s = 'Node({name}), offset({offset})\n'\
                .format(name=self.name,
                        offset=', '.join([str(o) for o in self.offsets]))
        s = s + '\tChannels:\n'
        for channel in self.channels:
            s = s + '\t\t' + channel.str() + '\n'
        for child in self.children:
            lines = child.str().split('\n')
            for line in lines:
                s = s + '\t' + line + '\n'
        return s



def parse_bvh_node(bvhlib_node):
    '''This function parses object from bvh-python (https://github.com/20tab/bvh-python)'''
    name = bvhlib_node.name
    offsets = [float(f) for f in bvhlib_node.children[0].value[1:]]
    channel_names = []
    for channels in bvhlib_node.filter('CHANNELS'):
        channel_names = [c for c in channels.value[2:]]
    children = []
    for c in bvhlib_node.filter('JOINT'):
        children.append(parse_bvh_node(c))
    node = BVHNode(name, offsets,
                   channel_names, children)
    return node

def render_frame(node, frame_data_array):
    for channel in node.channels:
        channel.set_value(frame_data_array.pop(0))
    for child in node.children:
        render_frame(child, frame_data_array)

def loads(s):
    bvhlib = BVHLIB.Bvh(s)
    root = parse_bvh_node(bvhlib.get_joints()[0])
    render_frame(root, [float(f) for f in bvhlib.frames[0]])
    return root, [[float(f) for f in frame] for frame in bvhlib.frames], bvhlib.frame_time

def load(file_path):
    with open(file_path, 'r') as f:
        return loads(f.read())
        

