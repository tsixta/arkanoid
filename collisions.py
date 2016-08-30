from math import sqrt, fabs, pi, acos
import numpy as np
#from enum import Enum


class HitObject():
    nothing = 0
    wall = 1
    board = 2
    brick = 3


class CollisionProperties:
    t = 2
    new_ball_angle = 0
    ball_center_position = np.array([0.0, 0.0])
    hit_object = HitObject.nothing
    brick_tx = -1
    brick_ty = -1

    def set(self, t, new_ball_angle, ball_center_position, hit_object, brick_tx=-1, brick_ty=-1):
        self.t = t
        self.new_ball_angle = new_ball_angle
        self.ball_center_position = ball_center_position
        self.hit_object = hit_object
        self.brick_tx = brick_tx
        self.brick_ty = brick_ty


def calculate_new_ball_angle_collision_horizontal_bar(old_angle):
    return -old_angle


def calculate_new_ball_angle_collision_vertical_bar(old_angle):
    return pi-old_angle


def vector_angle(vector):
    if vector[1] > 0:
        return acos(vector[0]/np.linalg.norm(vector))
    else:
        return -acos(vector[0] / np.linalg.norm(vector))

def calculate_new_ball_angle_collision_point(old_angle, point_circle_center_vector):
    # pv = [point_circle_center_vector[1], -point_circle_center_vector[0]]
    # norm_angle = acos(point_circle_center_vector[1] / np.linalg.norm(point_circle_center_vector))
    norm_angle = vector_angle([point_circle_center_vector[1], -point_circle_center_vector[0]])
    return calculate_new_ball_angle_collision_horizontal_bar(old_angle - norm_angle) + norm_angle


def moving_point_to_horizontal_bar(p, a, bar_x, bar_y, start_t):
    """
    Calculates time, when moving point hits a horizontal bar
    :param p: Initial coordinates of the point (list)
    :param a: Motion vector of the point (list)
    :param bar_x: Leftmost and right most coordinates of the bar (list)
    :param bar_y: Y coordinate of the bar (float)
    :param start_t: Time, when the point starts moving (0 <= start_t <= 1, float)
    :return: List [time, relative_x_position] if collision occurs, [2, -1] otherwise
    """
    ret = [2, -1]
    if fabs(a[1]) < 1e-10:
        if fabs(p[1] - bar_y) < 1e-10:
            ret = [0.5, 0.5]
    else:
        t = (bar_y - p[1]) / float(a[1])
        x = p[0] + a[0] * t
        if 0 <= t <= 1 - start_t and bar_x[0] <= x <= bar_x[1]:
            ret = [t, (x - bar_x[0]) / float(bar_x[1] - bar_x[0])]
    return ret


def moving_point_to_vertical_bar(p, a, bar_x, bar_y, start_t):
    """
    Calculates time, when moving point hits a vertical bar
    :param p: Initial coordinates of the point (list)
    :param a: Motion vector of the point (list)
    :param bar_x: X coordinate of the bar (float)
    :param bar_y: Topmost and bottommost coordinates of the bar (list)
    :param start_t: Time, when the point starts moving (0 <= start_t <= 1, float)
    :return: List [time, relative_y_position] if collision occurs, [2, -1] otherwise
    """
    ret = [2, -1]
    if fabs(a[0]) < 1e-10:
        if fabs(p[0] - bar_x) < 1e-10:
            ret = [0.5, 0.5]
    else:
        t = (bar_x - p[0]) / float(a[0])
        y = p[1] + a[1] * t
        if 0 <= t <= 1 - start_t and bar_y[0] <= y <= bar_y[1]:
            ret = [t, (y - bar_y[0]) / float(bar_y[1] - bar_y[0])]
    return ret


def moving_circle_to_horizontal_bar(orig_c, r, a, bar_x, bar_y, start_t):
    """
    Calculates time, when moving circle hits a horizontal bar
    :param orig_c: Initial coordinates of the center of the circle (list)
    :param r: Radius of the circle (float)
    :param a: Motion vector of the circle (list)
    :param bar_x: Leftmost and right most coordinates of the bar (list)
    :param bar_y: Y coordinate of the bar (float)
    :param start_t: Time, when the point starts moving (0 <= start_t <= 1, float)
    :return: List [time, relative_x_position, [absolute_ball_center_position]] if collision occurs, [2, -1, np.array([0, 0])] otherwise
    """
    ret = [2, -1, np.array([0, 0])]
    if a[1] <= 0:
        ret[0:2] = moving_point_to_horizontal_bar([orig_c[0], orig_c[1] - r], a, bar_x, bar_y, start_t)
    else:
        ret[0:2] = moving_point_to_horizontal_bar([orig_c[0], orig_c[1] + r], a, bar_x, bar_y, start_t)
    if ret[0] <= 1:
        ret[2] = orig_c + a * ret[0]
    return ret


def moving_circle_to_vertical_bar(orig_c, r, a, bar_x, bar_y, start_t):
    """
    Calculates time, when moving point hits a vertical bar
    :param orig_c: Initial coordinates of the center of the circle (list)
    :param r: Radius of the circle (float)
    :param a: Motion vector of the circle (list)
    :param bar_x: X coordinate of the bar (float)
    :param bar_y: Topmost and bottommost coordinates of the bar (list)
    :param start_t: Time, when the point starts moving (0 <= start_t <= 1, float)
    :return: List [time, relative_y_position, [absolute_ball_center_position]] if collision occurs, [2, -1, np.array([0, 0])] otherwise
    """
    ret = [2, -1, np.array([0, 0])]
    if a[0] <= 0:
        ret[0:2] = moving_point_to_vertical_bar([orig_c[0] - r, orig_c[1]], a, bar_x, bar_y, start_t)
    else:
        ret[0:2] = moving_point_to_vertical_bar([orig_c[0] + r, orig_c[1]], a, bar_x, bar_y, start_t)
    if ret[0] <= 1:
        ret[2] = orig_c + a * ret[0]
    return ret


def moving_point_to_circle(p, a, c, r, start_t):
    """
    Calculates time, when moving point hits a static circle.
    :param p: Initial coordinates of the point
    :param a: Motion vector of the point
    :param c: Coordinates of the center of the circle
    :param r: Radius of the circle
    :param start_t: Time, when the point starts moving (0 <= start_t <= 1)
    :return: 0 <= ret <=1 if collision occurs, 2 if does not
    """
    ret = 2
    axaxayay = float(a[0] ** 2 + a[1] ** 2)
    E = axaxayay * r ** 2 - (a[0] * (c[1] - p[1]) - a[1] * (c[0] - p[0])) ** 2
    if E >= 0.0 and fabs(axaxayay) > 1e-10:
        B = np.dot(a,c - p);
        t1 = (B + sqrt(E)) / axaxayay
        t2 = (B - sqrt(E)) / axaxayay
        if 0 <= t1 <= 1 - start_t and t1 < ret:
            ret = t1
        if 0 <= t2 <= 1 - start_t and t2 < ret:
            ret = t2
    return ret


def moving_circle_to_point(orig_c, r, a, p, start_t):
    """
    Calculates time, when moving circle hits a static point
    :param orig_c: Initial coordinates of the center of the circle
    :param r: Radius of the circle
    :param a: Motion vector of the circle
    :param p: Coordinates of the point
    :param start_t:
    :return: 0 <= ret <=1 if collision occurs, 2 if does not
    """
    return moving_point_to_circle(p, -a, orig_c, r, start_t)
    """
    axaxayay = float(ax ** 2 + ay ** 2)
    E = axaxayay * r ** 2 - (ax * (py - orig_cy) - ay * (px - orig_cx)) ** 2
    if E >= 0:
        B = ax * (px - orig_cx) + ay * (py - orig_cy)
        t1 = (B + sqrt(E)) / axaxayay
        t2 = (B - sqrt(E)) / axaxayay
        if start_t <= t1 <= 1 and t1 < ret:
            ret = t1
        if start_t <= t2 <= 1 and t2 < ret:
            ret = t2
    """
    # These two lines will be used in different part of the code
    #return ret


