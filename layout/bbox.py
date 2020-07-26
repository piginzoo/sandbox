import numpy as np
class BBox():
    def __init__(self, pos):
        assert pos.shape==(4,2)
        self.pos = pos

    def __str__(self):
        return self.pos.tolist()

    def __cmp__(self, other):
        me_y = self.pos[:,1].min()
        his_y = other[:,1].min()
        return me_y<his_y

    def sort(bbox_list):
        