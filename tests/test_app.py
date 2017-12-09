import os
import BeeVeeH

BVH_DIR = '%s/bvh_files' % os.path.dirname(__file__)

class TestCase():
    def test_bvh_play(self):
        file_path = '%s/0007_Cartwheel001.bvh' % BVH_DIR
        BeeVeeH.start(file_path, test=True)

if __name__ == '__main__':
    TestCase().test_bvh_play()
