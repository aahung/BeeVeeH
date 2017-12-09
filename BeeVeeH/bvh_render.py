from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

ChannelTransformFunctionMap = {
        'Xposition': lambda x: glTranslatef(x, 0.0, 0.0),
        'Yposition': lambda x: glTranslatef(0.0, x, 0.0),
        'Zposition': lambda x: glTranslatef(0.0, 0.0, x),
        'Xrotation': lambda x: glRotatef(x, 1.0, 0.0, 0.0),
        'Yrotation': lambda x: glRotatef(x, 0.0, 1.0, 0.0),
        'Zrotation': lambda x: glRotatef(x, 0.0, 0.0, 1.0)
    }

def render_connector(node):
    '''This function is inspired by 
    http://lifeofaprogrammergeek.blogspot.ca/2008/07/rendering-cylinder-between-two-points.html
    '''
    quadric=gluNewQuadric()
    subdivisions = 10
    radius = 1

    x1 = 0
    y1 = 0
    z1 = 0
    x2 = -node.offsets[0]
    y2 = -node.offsets[1]
    z2 = -node.offsets[2]

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

def render_end(node):
    glutSolidSphere(1, 20, 20);

def transform_channel(channel):
    ChannelTransformFunctionMap[channel.name](channel.value)

def render(node):
    glPushMatrix()
    glTranslatef(node.offsets[0],
                 node.offsets[1],
                 node.offsets[2]);
    
    render_end(node)
    render_connector(node)

    glPushMatrix()

    for channel in node.channels:
        transform_channel(channel)
    
    for child in node.children:
        render(child)

    glPopMatrix()
    glPopMatrix()