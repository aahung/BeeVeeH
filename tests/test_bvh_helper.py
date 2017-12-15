import os
import copy
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

    def check_bvh_node_above_ground(node):
        for child in node.children:
            assert(node.coordinates[1] >= 0) 
            TestCase.check_bvh_node_above_ground(child)

    def test_bvh_load_frame(self):
        file_path = '%s/rotate_hip.bvh' % BVH_DIR
        self.root, self.frames, self.frame_time = BVH.load(file_path)
        assert(len(self.frames) == 15)
        assert(self.frame_time == 1.8333)
        for frame in self.frames[0:1]:
            self.root.load_frame(frame)
            self.root.apply_transformation()
            print(self.root.str(True))
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
            TestCase.check_bvh_node_above_ground(self.root)

    def test_bvh_node_search(self):
        file_path = '%s/0007_Cartwheel001.bvh' % BVH_DIR
        self.root, self.frames, self.frame_time = BVH.load(file_path)
        assert(self.root.search_node('Head') != None)

    def set_all_weight_0(node):
        node.weight = 0
        for child in node.children:
            TestCase.set_all_weight_0(child)

    def test_bvh_node_distance(self):
        file_path = '%s/0007_Cartwheel001.bvh' % BVH_DIR
        self.root, self.frames, self.frame_time = BVH.load(file_path)
        root2 = copy.deepcopy(self.root)
        self.root.load_frame(self.frames[0])
        self.root.apply_transformation()
        root2.load_frame(self.frames[0])
        root2.apply_transformation()
        assert(BVH.BVHNode.distance(self.root, root2) == 0)
        root2.load_frame(self.frames[1])
        root2.apply_transformation()
        assert(BVH.BVHNode.distance(self.root, root2) > 0)
        assert(BVH.BVHNode.distance(self.root, root2) == self.root.frame_distance(self.frames[0], self.frames[1]))
        TestCase.set_all_weight_0(self.root)
        TestCase.set_all_weight_0(root2)
        assert(BVH.BVHNode.distance(self.root, root2) == 0)
