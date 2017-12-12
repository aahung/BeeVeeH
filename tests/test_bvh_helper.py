import os
import BeeVeeH
import BeeVeeH.bvh_helper as BVH
import pytest
import numpy as np

BVH_DIR = '%s/bvh_files' % os.path.dirname(__file__)

class TestCase():
    def test_bvh_parse(self):
        file_path = '%s/0007_Cartwheel001.bvh' % BVH_DIR
        self.root, self.frames, self.frame_time = BVH.load(file_path)
        assert(len(self.frames) == 2111)
        assert(self.frame_time == 0.008333)

    def check_bvh_node_distance_against_parent(node):
        for child in node.children:
            assert(abs(np.linalg.norm(child.offsets) - np.linalg.norm(node.coordinates - child.coordinates)) < 0.0001) 
            TestCase.check_bvh_node_distance_against_parent(child)

    def test_bvh_load_frame(self):
        file_path = '%s/rotate_hip.bvh' % BVH_DIR
        self.root, self.frames, self.frame_time = BVH.load(file_path)
        assert(len(self.frames) == 15)
        assert(self.frame_time == 1.8333)
        for frame in self.frames:
            self.root.load_frame(frame)
            self.root.apply_transformation()
            TestCase.check_bvh_node_distance_against_parent(self.root)

    def test_bvh_load_frame2(self):
        file_path = '%s/0007_Cartwheel001.bvh' % BVH_DIR
        self.root, self.frames, self.frame_time = BVH.load(file_path)
        assert(len(self.frames) == 2111)
        assert(self.frame_time == 0.008333)
        for frame in self.frames:
            self.root.load_frame(frame)
            self.root.apply_transformation()
            TestCase.check_bvh_node_distance_against_parent(self.root)