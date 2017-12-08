#!/usr/bin/env python3

import unittest
import sys
import os

sys.path = ['lib'] + sys.path

import bvh as BVH

BVH_DIR = '%s/bvh_files' % os.path.dirname(__file__)

class TestCase(unittest.TestCase):
    def test_bvh_parse(self):
        with open('%s/0005_2FeetJump001.bvh' % BVH_DIR, 'r') as f:
            bvh = BVH.Bvh(f.read())
            print([i for i in bvh.root])
        self.assertTrue(bvh is not None)
        self.assertTrue(len(bvh.frames) == 2575)
        self.assertTrue(isinstance(bvh.root, BVH.BvhNode))

if __name__ == '__main__':
    unittest.main()