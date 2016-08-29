import numpy as np
from math import radians, pi

class Board:
    length = 1.5
    position = np.array([7.0,23.0]) # units are tiles
    color = [127,127,127]
    last_drawn_rectangle = [0,0,1,1]
    hit_new_angle_span = radians(160.0)
    bonus = 1

    def get_ball_new_angle(self, hit_position):
        return -(pi / 2 + (0.5 - hit_position) * self.hit_new_angle_span)

