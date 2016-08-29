import numpy as np
from math import radians, floor, pi


def normalize_angle(angle_rad):
    return angle_rad-2*pi*floor(angle_rad/(2*pi))


class Ball:
    radius = 0.15  # horizontal tiles
    velocity = 5.0  # horizontal tiles per second
    angle = radians(-97.0)  # units are radians
    position = np.array([3.0,22.0])  # units are tiles
    board_position = 0.5  # used only before the game starts
    color = [255, 0, 0]
    last_drawn_rectangle = [0,0,1,1]

    def going_down(self):
        return 0.0 < normalize_angle(self.angle) < pi

    def going_up(self):
        return pi < normalize_angle(self.angle) < 2.0 * pi

    def going_left(self):
        return pi / 2.0 <= normalize_angle(self.angle) < 1.5 * pi

    def going_right(self):
        return 0.0 <= normalize_angle(self.angle) < pi / 2.0 or 1.5 * pi < normalize_angle(self.angle) <= 2.0 * pi
