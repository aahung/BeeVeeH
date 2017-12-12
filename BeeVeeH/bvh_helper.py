import bvh as BVHLIB
import math
import numpy as np

class BVHChannel(object):
    ChannelTransformMatrixMap = {
            'Xposition': lambda x: np.array([[1, 0, 0, x],
                                             [0, 1, 0, 0],
                                             [0, 0, 1, 0],
                                             [0, 0, 0, 1]]),
            'Yposition': lambda x: np.array([[1, 0, 0, 0],
                                             [0, 1, 0, x],
                                             [0, 0, 1, 0],
                                             [0, 0, 0, 1]]),
            'Zposition': lambda x: np.array([[1, 0, 0, 0],
                                             [0, 1, 0, 0],
                                             [0, 0, 1, x],
                                             [0, 0, 0, 1]]),
            'Xrotation': lambda x: np.array([[1, 0, 0, 0],
                                             [0, math.cos(math.radians(x)), -math.sin(math.radians(x)), 0],
                                             [0, math.sin(math.radians(x)), math.cos(math.radians(x)), 0],
                                             [0, 0, 0, 1]]),
            'Yrotation': lambda x: np.array([[math.cos(math.radians(x)), 0, math.sin(math.radians(x)), 0],
                                             [0, 1, 0, 0],
                                             [-math.sin(math.radians(x)), 0, math.cos(math.radians(x)), 0],
                                             [0, 0, 0, 1]]),
            'Zrotation': lambda x: np.array([[math.cos(math.radians(x)), -math.sin(math.radians(x)), 0, 0],
                                             [math.sin(math.radians(x)), math.cos(math.radians(x)), 0, 0],
                                             [0, 0, 1, 0],
                                             [0, 0, 0, 1]])
        }
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.value = 0.0

    def set_value(self, value):
        self.value = value

    def matrix(self):
        return BVHChannel.ChannelTransformMatrixMap[self.name](self.value)

    def str(self):
        return 'Channel({name}) = {value}'.format(name=self.name, value=self.value)

class BVHNode(object):
    def __init__(self, name, offsets, channel_names, children):
        super().__init__()
        self.name = name
        self.children = children # []
        self.channels = [BVHChannel(cn) for cn in channel_names] # []
        self.offsets = offsets # x, y, z

    def load_frame(self, frame_data_array):
        for channel in self.channels:
            channel.set_value(frame_data_array.pop(0))
        for child in self.children:
            child.load_frame(frame_data_array)

    def apply_transformation(self, parent_tran_matrix=np.identity(4)):
        self.coordinates = np.zeros((3,1))
        local_translation = np.array([[1, 0, 0, self.offsets[0]],
                                     [0, 1, 0, self.offsets[1]],
                                     [0, 0, 1, self.offsets[2]],
                                     [0, 0, 0, 1]])
        tran_matrix = np.identity(4)
        tran_matrix = np.dot(tran_matrix, parent_tran_matrix)
        tran_matrix = np.dot(tran_matrix, local_translation)
        for channel in self.channels:
            tran_matrix = np.dot(tran_matrix, channel.matrix())
        self.coordinates = np.dot(tran_matrix, np.append(self.coordinates, [[1]], axis=0))[:3]
        for child in self.children:
            child.apply_transformation(tran_matrix)

    def str(self, show_coordinates=False):
        s = 'Node({name}), offset({offset})\n'\
                .format(name=self.name,
                        offset=', '.join([str(o) for o in self.offsets]))
        if show_coordinates:
            try:
                s = s + '\tWorld coordinates: (%.2f, %.2f, %.2f)\n' % (self.coordinates[0],
                                                                       self.coordinates[1],
                                                                       self.coordinates[2])
            except Exception as e:
                print('World coordinates is not available, call apply_transformation() first')
        s = s + '\tChannels:\n'
        for channel in self.channels:
            s = s + '\t\t' + channel.str() + '\n'
        for child in self.children:
            lines = child.str(show_coordinates=show_coordinates).split('\n')
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

def loads(s):
    bvhlib = BVHLIB.Bvh(s)
    root = parse_bvh_node(bvhlib.get_joints()[0])
    return root, [[float(f) for f in frame] for frame in bvhlib.frames], bvhlib.frame_time

def load(file_path):
    with open(file_path, 'r') as f:
        return loads(f.read())
        

