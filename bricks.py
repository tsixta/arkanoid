import numpy as np
from commands import *


class Brick:
    type = 0  # type=0 is reserved for empty space
    last_drawn_rectangle = [0, 0, 1, 1]
    redraw = True
    can_be_destroyed = False

    def __init__(self, brick_type, drawn_rectangle):
        self.type = brick_type
        self.last_drawn_rectangle = drawn_rectangle


class BrickType:
    color = (0, 0, 255)
    # points = 20
    hit_commands = [(CommandTypes.destroy, ())]
    can_be_destroyed = False  # This is deduced automatically from the commands
    key_in_file = ''


