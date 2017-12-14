import os
import BeeVeeH
import pytest

BVH_DIR = '%s/bvh_files' % os.path.dirname(__file__)

class TestCase():
    def test_bvh_play(self):
        file_path = '%s/0007_Cartwheel001.bvh' % BVH_DIR
        if not BeeVeeH.start(file_path, test=True):
            pytest.skip('Cannot launch the app due to SystemExit, reason above')

if __name__ == '__main__':
    TestCase().test_bvh_play()
