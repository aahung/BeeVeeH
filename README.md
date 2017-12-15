# <img src='BeeVeeH-small.png' title='BeeVeeH' width='60' height='60' /> BeeVeeH - another BVH Player

[![Build Status](https://travis-ci.org/Aahung/BeeVeeH.svg?branch=master)](https://travis-ci.org/Aahung/BeeVeeH)
[![Coverage Status](https://coveralls.io/repos/github/Aahung/BeeVeeH/badge.svg?branch=master)](https://coveralls.io/github/Aahung/BeeVeeH?branch=master)
[![Dependency Status](https://beta.gemnasium.com/badges/github.com/Aahung/BeeVeeH.svg)](https://beta.gemnasium.com/projects/github.com/Aahung/BeeVeeH)
[![GitHub license](https://img.shields.io/github/license/Aahung/BeeVeeH.svg)](https://github.com/Aahung/BeeVeeH/blob/master/LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/aahung/beeveeh.svg)](https://github.com/Aahung/BeeVeeH/commits/master)
[![GitHub top language](https://img.shields.io/github/languages/top/aahung/beeveeh.svg)](#)
[![GitHub repo size in bytes](https://img.shields.io/github/repo-size/aahung/beeveeh.svg)](https://github.com/Aahung/BeeVeeH/archive/master.zip)
[![GitHub (Pre-)Release Date](https://img.shields.io/github/release-date-pre/aahung/beeveeh.svg)](https://github.com/Aahung/BeeVeeH/releases)

- Table of Content
  - [Development](#development)
    - [Requirements](#requirements)
    - [Setup](#setup)
    - [Test](#test)
    - [Run](#run)
  - [APIs](#apis)
    - [Quickstart](#quickstart)
    - [Functions](#functions)
    - [Class `BVH.BVHNode`](#class-bvhbvhnode)
    - [Class `BVH.BVHChannel`](#class-bvhbvhchannel)


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

#### macOS/Ubuntu
```sh
make init
```

This process will take a long time to finish on Ubuntu. If you want to speed up, you can try `make init-accelerated` to download my prebuilt pip packages (I have not built them for all platforms). 

#### Windows

```sh
pip install -r requirements.txt -t lib
```

### Test

#### macOS/Ubuntu
```sh
make test
```

#### Windows

```sh
$env:PYTHONPATH=".\lib"
python -m lib.pytest --ignore=lib
```

This will run the tests including playing a short sample BVH file.

### Run

#### macOS/Ubuntu
```sh
make run
```

#### Windows
```sh
python -m main
```

This is the launch the main entry of BeeVeeH.

or,

#### macOS/Ubuntu
```sh
make dist
```
#### Windows
```sh
$env:PYTHONPATH=""
pip install PyInstaller==3.3
PyInstaller BeeVeeH.spec
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
#     World coordinates: (18.94, 35.04, -9.44)
#     Channels:
#         Channel(Xposition) = 18.9393
#         Channel(Yposition) = 35.0369
#         Channel(Zposition) = -9.444
#         Channel(Xrotation) = 34.5666
#         Channel(Yrotation) = 71.8402
#         Channel(Zrotation) = -35.4585
#     Node(LeftUpLeg), offset(3.31716, 0.0, 0.0)
#         World coordinates: (19.78, 34.91, -12.65)
#         Channels:
#             Channel(Xrotation) = -5.7958
#             Channel(Yrotation) = 9.0163
#             Channel(Zrotation) = -0.8796
#         Node(LeftLeg), offset(0.0, -16.62131, 0.0)
#             World coordinates: (18.36, 18.36, -12.10)
#             Channels:
#                 Channel(Xrotation) = 9.3583
#                 ...

print(root.search_node('Head').str(show_coordinates=True))
# Node(Head), offset(0.0, 6.84636, 0.0)
#     World coordinates: (23.03, 59.50, -10.77)
#     Channels:
#         Channel(Xrotation) = -5.4518
#         Channel(Yrotation) = -2.1447
#         Channel(Zrotation) = -0.3752

node = root.children[1]
print('The world coordinates of JOINT %s at frames[4] is (%.2f, %.2f, %.2f)' \
	   % (node.name, node.coordinates[0], 
	      node.coordinates[1], node.coordinates[2]))
# The world coordinates of JOINT RightUpLeg at frames[4] is (18.10, 35.16, -6.24)


root.frame_distance(frames[0], frames[0])
# 0.0

root.frame_distance(frames[0], frames[1])
# 7.5706251988920146

root.search_node('Head').weight = 100.0
root.frame_distance(frames[0], frames[1])
# 34.952071657201969
```


### Functions

#### `BVH.loads`(string): (`BVH.BVHNode`, `[[float]]`, `float`)

> `BVH.loads()` will parse a string (in BVH format) and return the root node, frames and time between two frames. Each frame is one sample of motion data in the form of a float list. The float numbers appear in the order of the channels.

#### `BVH.load`(file_path): (`BVH.BVHNode`, `[[float]]`, `float`)

> `BVH.load()` will parse a BVH file and return the root node, frames and time between two frames. Refer to `BVH.loads` for more details.



### Class `BVH.BVHNode`

#### Properties

##### `name`: `string` 

> the name of the node.

##### `children`: `[BVH.BVHNode]` 

> the list of children nodes.

##### `channels`: `[BVH.BVHChannel]` 

> the list of channels. Accessing `channel.value` requires calling `BVH.BVHNode.load_frame()` first.

##### `offsets`: `[float]` 

> the offsets, in the form of [x, y, z].

##### `coordinates`: `numpy.ndarray`

> the world coordinates, with shape=(3, 1). Accessing it requires calling `BVH.BVHNode.load_frame()` and `BVH.BVHNode.apply_transformation()` first.

##### `weight`: `float`

> the weight for frame distance calculation.

#### Methods

##### `__init__`(self, name, offsets, channel_names, children)

> Constructor. 

##### `search_node`(self, name): `BVH.BVHNode`

> `search_node` searches node recursively by name, returns `None` if not found.

##### `load_frame`(self, frame\_data_array)

> `load_frame()` assigns a frame. It will map the motion data to each channel. You can get the list of "frame\_data_array" from `BVH.load()` or `BVH.loads()`.

##### `apply_transformation`(self, parent\_tran\_matrix=np.identity(4))

> `apply_transformation()` starts the calculation of world coordinates. Call this method on the root BVHNode only (no parameter needed).

##### `str`(self, show_coordinates=False): `string`

> `str()` returns a readable string containing information about the node and its childrens. Before setting `show_coordinates=True`, make sure call `BVH.BVHNode.load_frame()` and `BVH.BVHNode.apply_transformation()` first.

##### `frame_distance`(self, frame_a, frame_b): `float`

> `frame_distance` calculates the Euclidean distances of all joints between two frames, and returns the weighted sum.



### Class `BVH.BVHChannel`

#### Properties

##### `name`: `string`

> the name of the channel.

##### `value`: `float`

> the value of the channel, in degree when the channel represents a rotation. Accessing it requires calling `BVH.BVHNode.load_frame()` first.

#### Methods

##### `__init__`(self, name)

> Constructor.

##### `set_value`(self, value)

> `set_value()` is the setter for `value`.

##### `matrix`(self): `numpy.ndarray`

> `matrix()` returns the transformation matrix of the channel.

##### `str`(self)

> `str()` returns a readable string containing information about the channel.
