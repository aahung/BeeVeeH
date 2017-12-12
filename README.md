# <img src='BeeVeeH-small.png' title='BeeVeeH' width='60' height='60' /> BeeVeeH - another BVH Player

[![Build Status](https://travis-ci.org/Aahung/BeeVeeH.svg?branch=master)](https://travis-ci.org/Aahung/BeeVeeH)

![BeeVeeH Screenshot](screenshot.png)

## Development

### Requirements

- Python 3.x
- pip (>= 9.0.1, due to the [bugs in early pip versions](https://github.com/pypa/pip/issues/3826), please make sure the version of pip  is 9.0.1 or above by `pip3 --version`)

If you are using macOS, you can skip this. If you are using Ubuntu, please do the following setups.

#### Ubuntu prerequisites

Install the following packages via `apt`:

- libwebkitgtk-dev
- libjpeg-dev
- libtiff-dev
- libgtk2.0-dev
- libsdl1.2-dev
- libgstreamer-plugins-base0.10-dev
- freeglut3
- freeglut3-dev
- libnotify-dev
- libsm-dev
- libgtk-3-dev
- libwebkitgtk-3.0-dev

### Setup


```sh
make init
```

This process will take a long time to finish. If you want to speed up, you can try `make init-accelerated` to download my prebuilt pip packages (I have not built them for all platforms).

### Test

```sh
make test
```

This will play a short sample BVH file. After completion, BeeVeeH will close automatically.

### Run

```sh
make run
```

This is the launch the main entry of BeeVeeH.

or,

```sh
make dist
```

This will generate the packed BeeVeeH inside the `./dist` directory.

## APIs

You might find BeeVeeH's classes `BVHNode` and `BVHChannel` useful for parsing and world coordinate extraction. 

### Quickstart

```py
import BeeVeeH.bvh_helper as BVH


file_path = 'tests/bvh_files/0007_Cartwheel001.bvh'
root, frames, frame_time = BVH.load(file_path)
print('number of frame = %d' % len(frames))
# "number of frame = 2111"

root.load_frame(frames[4])
root.apply_transformation()
print(root.str(show_coordinates=True))

# Node(Hips), offset(0.0, 0.0, 0.0)
#     World coordinates: (0.00, 0.00, 0.00)
#     Channels:
#         Channel(Xposition) = 18.9393
#         Channel(Yposition) = 35.0369
#         Channel(Zposition) = -9.444
#         Channel(Xrotation) = 34.5666
#         Channel(Yrotation) = 71.8402
#         Channel(Zrotation) = -35.4585
#     Node(LeftUpLeg), offset(3.31716, 0.0, 0.0)
#         World coordinates: (0.84, -0.60, -3.15)
#         Channels:
#             Channel(Xrotation) = -5.7958
#             Channel(Yrotation) = 9.0163
#             Channel(Zrotation) = -0.8796
#         Node(LeftLeg), offset(0.0, -16.62131, 0.0)
#             World coordinates: (-14.40, -6.55, -6.09)
#             Channels:
#                 Channel(Xrotation) = 9.3583
#                 Channel(Yrotation) = -0.0
#                 Channel(Zrotation) = 0.0


node = root.children[1]
print('The world coordinates of JOINT %s at frames[4] is (%.2f, %.2f, %.2f)' \
	   % (node.name, node.coordinates[0], 
	      node.coordinates[1], node.coordinates[2]))

# The world coordinates of JOINT RightUpLeg at frames[4] is (-0.84, 0.60, 3.15)
```

### Functions

`BVH.loads`(string)

`BVH.load`(file_path)

### Class BVH.BVHNode

#### Properties

`name`

`children`

`channels`

`offsets`

`coordinates`

#### Methods
`__init__`(self, name, offsets, channel_names, children)

`load_frame`(self, frame\_data_array)

`apply_transformation`(self, parent\_tran\_matrix=np.identity(4), parent_coordinates=np.zeros((3,1)))

`str`(self, show_coordinates=False)

### Class BVH.BVHChannel

#### Properties

`name`

`value`

#### Methods

`__init__`(self, name)

`set_value`(self, value)

`matrix`(self)

`str`(self)
