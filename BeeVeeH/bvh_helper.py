import bvh as BVHLIB

class BVHChannel(object):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.value = 0.0

    def set_value(self, value):
        self.value = value

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

def loads(s):
    bvhlib = BVHLIB.Bvh(s)
    root = parse_bvh_node(bvhlib.get_joints()[0])
    return root, [[float(f) for f in frame] for frame in bvhlib.frames], bvhlib.frame_time

def load(file_path):
    with open(file_path, 'r') as f:
        return loads(f.read())
        

