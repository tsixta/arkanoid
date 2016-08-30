from collisions import *
from math import sin, cos, floor, ceil
import numpy as np
from board import Board
from ball import Ball, normalize_angle
from bricks import Brick, BrickType
from commands import *
import ast
from random import random
#from enum import Enum


class EventType():
    ball = set([0])


class Level:
    screen_size = [320,200]
    tiles = [10,204]
    background_color = [255,255,255]
    score_color = [0, 0, 0]
    board = Board()
    ball = Ball()
    bricks = []
    brick_types = [None]
    total_elapsed_time_seconds = 0.0
    command_queue = []
    force_redraw_all = True
    game_started = False
    paused = False
    score = 0
    defeated = False
    won = False

    def initialize(self, game, screen, ball_board_position = -1.0):
        self.game_started = False
        if 0.0 <= ball_board_position <= 1.0:
            self.ball.board_position = ball_board_position
        else:
            self.ball.board_position = random()
        self.ball.angle = pi / 2.0
        self.redraw(game,screen, self.screen_size[0]/2, 0)
        for x in range(self.tiles[0]):
            for y in range(self.tiles[1]):
                if self.bricks[x][y].type > 0:
                    self.__redraw_brick(game, screen, x, y)
        return self.screen_size[0]/2

    def start_game(self):
        self.game_started = True

    def load(self, filename):
        f = open(filename, 'r')
        loading_bricks = False
        self.brick_types = [None]
        row = 0
        for line in f:
            line = line.strip()
            if len(line) > 0:
                if loading_bricks and row < self.tiles[1]:
                    data = line.split(',')
                    for col, b in enumerate(data):
                        self.bricks[col][row].type = self.brick_type_index(b)
                        if self.bricks[col][row].type != 0:
                            self.bricks[col][row].can_be_destroyed = self.brick_types[self.bricks[col][row].type].can_be_destroyed
                        else:
                            self.bricks[col][row].can_be_destroyed = False
                    row += 1
                else:
                    command, arguments = parse_line(line)
                    if command == 'screen.size':
                        self.screen_size = ast.literal_eval(arguments)
                    if command == 'tiles':
                        self.tiles = ast.literal_eval(arguments)
                        self.board.position = [self.tiles[0]/2, self.tiles[1]-1]
                    if command == 'board.length':
                        self.board.length = float(ast.literal_eval(arguments))
                    if command == 'board.color':
                        self.board.color = ast.literal_eval(arguments)
                    if command == 'ball.radius':
                        self.ball.radius = float(ast.literal_eval(arguments))
                    if command == 'ball.color':
                        self.ball.color = ast.literal_eval(arguments)
                    if command == 'ball.initial_speed':
                        self.ball.velocity = float(ast.literal_eval(arguments))
                    if command == 'background.color':
                        self.background_color = ast.literal_eval(arguments)
                    if command == 'score.color':
                        self.score_color = ast.literal_eval(arguments)
                    if command == 'add_brick_type':
                        arguments = ast.literal_eval(preprocess_brick_type(arguments))
                        bid = self.brick_type_index(arguments[0])
                        if bid <= 0:
                            self.brick_types.append(BrickType())
                            bid = len(self.brick_types) - 1
                        self.brick_types[bid].key_in_file = str(arguments[0])
                        self.brick_types[bid].color = arguments[1]
                        self.brick_types[bid].hit_commands = []

                        for c in arguments[2:]:
                            execute_if_events = set([0])
                            generate_events = set([0])
                            if c[0] == int(CommandTypes.add_points): #destroy(execute_if_events=0)
                                if len(c) > 2:
                                    execute_if_events = convert_to_set(c[2])
                                self.brick_types[bid].hit_commands.extend([(CommandTypes.add_points, [c[1], execute_if_events])])
                            if c[0] == int(CommandTypes.destroy): #destroy(execute_if_events=0)
                                if len(c) > 1:
                                    execute_if_events = convert_to_set(c[1])
                                self.brick_types[bid].hit_commands.extend([(CommandTypes.destroy, [execute_if_events])])
                                self.brick_types[bid].can_be_destroyed = True
                            if c[0] == int(CommandTypes.change_brick_type): #change_type(new_type, execute_if_events=0)
                                if len(c) > 2:
                                    execute_if_events = convert_to_set(c[2])
                                self.brick_types[bid].hit_commands.extend([(CommandTypes.change_brick_type, [c[1], execute_if_events])])
                                self.brick_types[bid].can_be_destroyed = True
                            if c[0] == int(CommandTypes.delay): #delay(milliseconds, execute_if_events=0)
                                if len(c) > 2:
                                    execute_if_events = convert_to_set(c[2])
                                self.brick_types[bid].hit_commands.extend([(CommandTypes.delay, [c[1], execute_if_events])])
                            if c[0] == int(CommandTypes.hit_brick): #hit(dx, dy, execute_if_events=0, generate_events=0)
                                if len(c) > 3:
                                    generate_events = convert_to_set(c[3])
                                if len(c) > 4:
                                    execute_if_events = convert_to_set(c[4])
                                self.brick_types[bid].hit_commands.extend([(CommandTypes.hit_brick, [c[1], c[2], generate_events, execute_if_events])])
                    if command == 'bricks':
                        self.bricks = [[Brick(0, self.tile_to_pixels_rectangle([x, y])) for y in range(self.tiles[1])]
                                       for x in range(self.tiles[0])]
                        loading_bricks = True

    def player_defeated(self):
        self.defeated = True
        self.paused = True

    def check_for_victory(self):
        ret = True
        for x in range(self.tiles[0]):
            for y in range(self.tiles[1]):
                ret = ret and not self.bricks[x][y].can_be_destroyed
        if ret:
            self.won = True
            self.paused = True
        return ret

    def redraw(self, game, screen, mouse_x, elapsed_time):
        if self.paused:
            ret = [0, 0, self.screen_size[0], self.screen_size[1]]
            for x in range(self.tiles[0]):
                for y in range(self.tiles[1]):
                    self.__redraw_brick(game, screen, x, y)
            self.__draw_score(game, screen)
            if self.defeated:
                self.__draw_defeat_text(game,screen)
            if self.won:
                self.__draw_victory_text(game, screen)

        else:
            ret = []
            if not game.display.get_active() or not self.game_started:
                self.force_redraw_all = True
            screen.fill(self.background_color)
            ret.extend(self.__move_board(game, screen, mouse_x))
            if self.game_started:
                ret.extend(self.__move_ball(game, screen, elapsed_time))
                self.total_elapsed_time_seconds += elapsed_time
                self.__process_command_queue(self.total_elapsed_time_seconds)
            else:
                ret.extend(self.__draw_ball_on_the_board(game, screen))

            if self.force_redraw_all and game.display.get_active():
                self.force_redraw_all = False
                for x in range(self.tiles[0]):
                    for y in range(self.tiles[1]):
                        self.bricks[x][y].redraw = True
            for x in range(self.tiles[0]):
                for y in range(self.tiles[1]):
                    if self.bricks[x][y].redraw:
                        ret.extend(self.__redraw_brick(game, screen, x, y))
                        self.bricks[x][y].redraw = False
            ret.extend(self.__draw_score(game, screen))
            self.check_for_victory()

        return ret

    def __draw_defeat_text(self, game, screen):
        font = game.font.Font(None, int(self.screen_size[0] / 4))
        text = font.render("Defeat!", 1, self.score_color)
        textpos = text.get_rect()
        ret = [[int((self.screen_size[0]-textpos[2])/2), int((self.screen_size[1]-textpos[3]) / 2), textpos[2], textpos[3]]]
        screen.blit(text, (ret[0][0], ret[0][1]))
        return ret

    def __draw_victory_text(self, game, screen):
        font = game.font.Font(None, int(self.screen_size[0] / 4))
        text = font.render("Victory!", 1, self.score_color)
        textpos = text.get_rect()
        ret = [[int((self.screen_size[0]-textpos[2])/2), int((self.screen_size[1]-textpos[3]) / 2), textpos[2], textpos[3]]]
        screen.blit(text, (ret[0][0], ret[0][1]))
        return ret

    def __draw_score(self, game, screen):
        font = game.font.Font(None, 36)
        text = font.render(str(self.score), 1, self.score_color)
        textpos = text.get_rect()
        ret = [[self.screen_size[0]-textpos[2], 0, textpos[2], textpos[3]]]
        screen.blit(text, (ret[0][0], ret[0][1]))
        return ret

    def __redraw_brick(self, game, screen, x, y):
        brick_type = self.bricks[x][y].type
        if brick_type > 0:
            game.draw.rect(screen, self.brick_types[brick_type].color, self.bricks[x][y].last_drawn_rectangle, 0)
        return [self.bricks[x][y].last_drawn_rectangle]

    def __move_board(self, game, screen, mouse_x):
        hbl = float(self.board.length) / 2
        new_tx_position = self.pixels_to_tiles_x(mouse_x)
        if new_tx_position + hbl > self.tiles[0]:
            new_tx_position = self.tiles[0] - hbl
        if new_tx_position - hbl < 0:
            new_tx_position = hbl
        #  resolve potential collision with the ball. If a collision happens, change the ball's motion vector here
        ret = [self.board.last_drawn_rectangle]
        new_rectangle = (self.tiles_to_pixels_x(float(new_tx_position) - hbl),
                         self.tiles_to_pixels_y(self.board.position[1]),
                         self.tiles_to_pixels_x(self.board.length),
                         self.tiles_to_pixels_y(1.0))
        game.draw.rect(screen, self.board.color, new_rectangle, 0)
        ret.append(new_rectangle)
        self.board.last_drawn_rectangle=new_rectangle
        return ret

    def __set_bricks_around_ball_to_redraw(self):
        yradius = self.horizontal_tiles_to_vertical_tiles(self.ball.radius)
        start_x = int(max(0,floor(self.ball.position[0] - self.ball.radius)-1))
        end_x = int(min(self.tiles[0], ceil(self.ball.position[0] + self.ball.radius)+2))
        start_y = int(max(0,floor(self.ball.position[1] - yradius)-1))
        end_y = int(min(self.tiles[1], ceil(self.ball.position[1] + yradius)+2))
        for x in range(start_x,end_x):
            for y in range(start_y, end_y):
                if self.bricks[x][y].type != 0:
                    self.bricks[x][y].redraw = True

    def __draw_ball_on_the_board(self, game, screen):
        ret = [self.ball.last_drawn_rectangle]
        radius_px = self.tiles_to_pixels_x(self.ball.radius)
        position_px = [
            self.board.last_drawn_rectangle[0] + self.ball.board_position * self.board.last_drawn_rectangle[2],
            self.board.last_drawn_rectangle[1] - radius_px - 1]
        self.ball.position = self.pixels_to_tiles(position_px)

        position_px = map(int, position_px)
        new_rectangle = (position_px[0] - radius_px - 1,
                         position_px[1] - radius_px - 1,
                         2 * (radius_px + 1),
                         2 * (radius_px + 1))
        ret.append(new_rectangle)
        game.draw.circle(screen, self.ball.color, position_px, int(radius_px), 0)
        self.ball.last_drawn_rectangle = new_rectangle
        self.__set_bricks_around_ball_to_redraw()
        return ret


    def __move_ball(self, game, screen, elapsed_time):
        ret = [self.ball.last_drawn_rectangle]
        self.__set_bricks_around_ball_to_redraw()
        #  resolve collisions
        start_t = 0
        cp = CollisionProperties()
        velocity = self.tiles_to_pixels_x(self.ball.velocity * elapsed_time)
        position_px = self.tiles_to_pixels(self.ball.position)
        radius_px = self.tiles_to_pixels_x(self.ball.radius)
        while start_t <= 1.0:
            cp.t = 2
            a = np.array([velocity * cos(self.ball.angle), velocity * sin(self.ball.angle)])
            #  walls
            if np.linalg.norm(a) > 1e-5 and position_px[1] <= self.board.last_drawn_rectangle[1]:
                self.__collisions_walls(cp, position_px, radius_px, a, start_t)
            #  board
            if self.ball.going_down():
                self.__collisions_board(cp, position_px, radius_px, a, start_t)
            #  bricks
            for x in range(self.tiles[0]):
                for y in range(self.tiles[1]):
                    if self.bricks[x][y].type > 0:
                        self.__collisions_brick(cp, position_px, radius_px, a, start_t, x, y)
            # change ball direction if a collision occurred and calculate new ball's position
            if cp.t <= 1:
                position_px = cp.ball_center_position
                self.ball.angle = cp.new_ball_angle
            else:
                position_px = position_px + (1 - start_t) * a
            if position_px[1] > self.board.last_drawn_rectangle[1]:
                self.player_defeated()
            start_t = cp.t
            if cp.hit_object == HitObject.brick:
                self.__process_brick_hit_commands(cp.brick_tx, cp.brick_ty, self.total_elapsed_time_seconds + cp.t, EventType.ball)
            elif cp.hit_object == HitObject.board:
                self.board.bonus -= 1
                if self.board.bonus > 0:
                    self.board.bonus = 0
            cp.hit_object = HitObject.nothing
        #  redraw ball

        self.ball.position = self.pixels_to_tiles(position_px)

        position_px = map(int,position_px)
        new_rectangle = (position_px[0] - radius_px - 1,
                         position_px[1] - radius_px - 1,
                         2 * (radius_px + 1),
                         2 * (radius_px + 1))
        ret.append(new_rectangle)
        game.draw.circle(screen, self.ball.color, position_px, int(radius_px), 0)
        self.ball.last_drawn_rectangle = new_rectangle
        self.__set_bricks_around_ball_to_redraw()
        return ret

    def __process_command_queue(self, time):
        self.command_queue[:] = [c for c in self.command_queue if not (c.timestamp <= time and self.__eval_command(c.type, c.parameters, time))]


    def __process_brick_hit_commands(self, tx, ty, time, events):
        execution_time = time
        self.bricks[tx][ty].redraw = True
        if self.bricks[tx][ty].type != 0:
            for command, parameters in self.brick_types[self.bricks[tx][ty].type].hit_commands:
                if len(parameters[-1] & events) > 0:
                    if command == CommandTypes.add_points:
                        if execution_time > time:
                            self.command_queue.append(Command(CommandTypes.add_points, [parameters[0] + self.board.bonus], execution_time))
                        else:
                            self.__eval_command(CommandTypes.add_points, [parameters[0] + self.board.bonus], execution_time)
                    elif command == CommandTypes.destroy:
                        if execution_time > time:
                            self.command_queue.append(Command(CommandTypes.change_brick_type, [tx, ty, 0], execution_time))
                        else:
                            self.__eval_command(CommandTypes.change_brick_type, [tx, ty, 0], execution_time)
                    elif command == CommandTypes.change_brick_type:
                        if execution_time > time:
                            self.command_queue.append(Command(CommandTypes.change_brick_type, [tx, ty, parameters[0]], execution_time))
                        else:
                            self.__eval_command(CommandTypes.change_brick_type, [tx, ty, parameters[0]], execution_time)
                    elif command == CommandTypes.hit_brick:
                        target_tx = parameters[0] + tx
                        target_ty = parameters[1] + ty
                        if 0 <= target_tx < self.tiles[0] and 0 <= target_ty < self.tiles[1] and self.bricks[target_tx][target_ty].type != 0:
                            if execution_time > time:
                                self.command_queue.append(Command(CommandTypes.hit_brick, [target_tx, target_ty, parameters[-2]], execution_time))
                            else:
                                self.__process_brick_hit_commands(target_tx, target_ty, execution_time, parameters[-2])
                    elif command == CommandTypes.delay:
                        execution_time += parameters[0] / 1000.0
                    elif command == CommandTypes.noop:
                        pass
                    else:
                        print "Warning: Unknown command: ", command

    def __eval_command(self, command, parameters, time):
        if command == CommandTypes.change_brick_type and self.bricks[parameters[0]][parameters[1]].type != 0:
            self.board.bonus += 1
            self.bricks[parameters[0]][parameters[1]].type = parameters[2]
            self.bricks[parameters[0]][parameters[1]].redraw = True
            if self.bricks[parameters[0]][parameters[1]].type == 0:
                self.bricks[parameters[0]][parameters[1]].can_be_destroyed = False
        elif command == CommandTypes.hit_brick and self.bricks[parameters[0]][parameters[1]].type != 0:
            self.__process_brick_hit_commands(parameters[0], parameters[1], time, parameters[-1])
            self.bricks[parameters[0]][parameters[1]].redraw = True
        elif command == CommandTypes.add_points:
            self.score += parameters[0]
        return True

    def __collisions_brick(self, cp, position_px, radius_px, a, start_t, tx, ty):
        ldr = self.bricks[tx][ty].last_drawn_rectangle
        normalized_ball_angle = normalize_angle(self.ball.angle)
        if self.ball.going_down():
            c = moving_circle_to_horizontal_bar(position_px, radius_px, a, [ldr[0], ldr[0] + ldr[2]], ldr[1], start_t)
            if c[0] < cp.t:
                cp.set(c[0], calculate_new_ball_angle_collision_horizontal_bar(normalized_ball_angle), c[2], HitObject.brick, tx, ty)
        if self.ball.going_up():
            c = moving_circle_to_horizontal_bar(position_px, radius_px, a, [ldr[0], ldr[0] + ldr[2]], ldr[1] + ldr[3], start_t)
            if c[0] < cp.t:
                cp.set(c[0], calculate_new_ball_angle_collision_horizontal_bar(normalized_ball_angle), c[2], HitObject.brick, tx, ty)
        if self.ball.going_right():
            c = moving_circle_to_vertical_bar(position_px, radius_px, a, ldr[0], [ldr[1], ldr[1] + ldr[3]], start_t)
            if c[0] < cp.t:
                cp.set(c[0], calculate_new_ball_angle_collision_vertical_bar(normalized_ball_angle), c[2], HitObject.brick, tx, ty)
        if self.ball.going_left():
            c = moving_circle_to_vertical_bar(position_px, radius_px, a, ldr[0] + ldr[2], [ldr[1], ldr[1] + ldr[3]], start_t)
            if c[0] < cp.t:
                cp.set(c[0], calculate_new_ball_angle_collision_vertical_bar(normalized_ball_angle), c[2], HitObject.brick, tx, ty)
        if self.ball.going_down() or self.ball.going_right():
            p = np.array([ldr[0], ldr[1]])
            c = moving_circle_to_point(position_px, radius_px, a, p, start_t)
            if c < cp.t:
                new_ball_center = position_px + c * a
                if 0.5 * pi <= normalized_ball_angle <= pi and self.ball.going_down():
                    cp.set(c, calculate_new_ball_angle_collision_horizontal_bar(normalized_ball_angle), new_ball_center, HitObject.brick, tx, ty)
                elif (1.5 * pi <= normalized_ball_angle <= 2.0 * pi or normalized_ball_angle == 0) and self.ball.going_right():
                    cp.set(c, calculate_new_ball_angle_collision_vertical_bar(normalized_ball_angle), new_ball_center, HitObject.brick, tx, ty)
                elif 0.0 < normalized_ball_angle < 0.5 * pi:
                    cp.set(c, calculate_new_ball_angle_collision_vertical_bar(normalized_ball_angle - pi / 4.0) + pi / 4.0, new_ball_center, HitObject.brick, tx, ty)
        if self.ball.going_down() or self.ball.going_left():
            p = np.array([ldr[0] + ldr[2], ldr[1]])
            c = moving_circle_to_point(position_px, radius_px, a, p, start_t)
            if c < cp.t:
                new_ball_center = position_px + c * a
                if 0.0 <= normalized_ball_angle <= 0.5 * pi and self.ball.going_down():
                    cp.set(c, calculate_new_ball_angle_collision_horizontal_bar(normalized_ball_angle), new_ball_center, HitObject.brick, tx, ty)
                elif pi <= normalized_ball_angle <= 1.5 * pi and self.ball.going_left():
                    cp.set(c, calculate_new_ball_angle_collision_vertical_bar(normalized_ball_angle), new_ball_center, HitObject.brick, tx, ty)
                elif 0.5 * pi < normalized_ball_angle < pi:
                    cp.set(c, calculate_new_ball_angle_collision_vertical_bar(normalized_ball_angle + pi / 4.0) - pi / 4.0, new_ball_center, HitObject.brick, tx, ty)
        if self.ball.going_up() or self.ball.going_right():
            p = np.array([ldr[0], ldr[1] + ldr[3]])
            c = moving_circle_to_point(position_px, radius_px, a, p, start_t)
            if c < cp.t:
                new_ball_center = position_px + c * a
                if pi <= normalized_ball_angle <= 1.5 * pi and self.ball.going_up():
                    cp.set(c, calculate_new_ball_angle_collision_horizontal_bar(normalized_ball_angle), new_ball_center, HitObject.brick, tx, ty)
                elif 0.0 <= normalized_ball_angle <= 0.5 * pi and self.ball.going_right():
                    cp.set(c, calculate_new_ball_angle_collision_vertical_bar(normalized_ball_angle), new_ball_center, HitObject.brick, tx, ty)
                elif 1.5 < normalized_ball_angle < 2.0 * pi or normalized_ball_angle == 2.0:
                    cp.set(c, calculate_new_ball_angle_collision_vertical_bar(normalized_ball_angle + pi / 4.0) - pi / 4.0, new_ball_center, HitObject.brick, tx, ty)
        if self.ball.going_up() or self.ball.going_left():
            p = np.array([ldr[0] + ldr[2], ldr[1] + ldr[3]])
            c = moving_circle_to_point(position_px, radius_px, a, p, start_t)
            if c < cp.t:
                new_ball_center = position_px + c * a
                if (1.5 * pi <= normalized_ball_angle <= 2.0 * pi or normalized_ball_angle == 0.0) and self.ball.going_up():
                    cp.set(c, calculate_new_ball_angle_collision_horizontal_bar(normalized_ball_angle), new_ball_center, HitObject.brick, tx, ty)
                elif 0.5 * pi <= normalized_ball_angle <= pi and self.ball.going_left():
                    cp.set(c, calculate_new_ball_angle_collision_vertical_bar(normalized_ball_angle), new_ball_center, HitObject.brick, tx, ty)
                elif pi < normalized_ball_angle < 1.5 * pi:
                    cp.set(c, calculate_new_ball_angle_collision_vertical_bar(normalized_ball_angle - pi / 4.0) + pi / 4.0, new_ball_center, HitObject.brick, tx, ty)

    def __collisions_board(self, cp, position_px, radius_px, a, start_t):
        c = moving_circle_to_horizontal_bar(position_px, radius_px, a, [self.board.last_drawn_rectangle[0],
                                                                        self.board.last_drawn_rectangle[0] +
                                                                        self.board.last_drawn_rectangle[2]],
                                            self.board.last_drawn_rectangle[1], start_t)
        if c[0] < cp.t:
            cp.set(c[0], self.board.get_ball_new_angle(c[1]), c[2], HitObject.board)

        c = moving_circle_to_point(position_px, radius_px, a,
                                   [self.board.last_drawn_rectangle[0], self.board.last_drawn_rectangle[1]], start_t)
        if c < cp.t:
            hit_position = position_px + a * c
            if hit_position[1] <= self.board.last_drawn_rectangle[1]:
                cp.set(c, self.board.get_ball_new_angle(0.0), hit_position, HitObject.board)
            else:
                cp.set(c, calculate_new_ball_angle_collision_vertical_bar(self.ball.angle), hit_position, HitObject.board)

        c = moving_circle_to_point(position_px, radius_px, a,
                                   [self.board.last_drawn_rectangle[0] + self.board.last_drawn_rectangle[2],
                                    self.board.last_drawn_rectangle[1]], start_t)
        if c < cp.t:
            hit_position = position_px + a * c
            if hit_position[1] <= self.board.last_drawn_rectangle[1]:
                cp.set(c, self.board.get_ball_new_angle(1.0), hit_position, HitObject.board)
            else:
                cp.set(c, calculate_new_ball_angle_collision_vertical_bar(self.ball.angle), hit_position, HitObject.board)

    def __collisions_walls(self, cp, position_px, radius_px, a, start_t):
        #  top wall
        if self.ball.going_up():
            c = moving_circle_to_horizontal_bar(position_px, radius_px, a, [0, self.screen_size[0]], 0, start_t)
            if c[0] < cp.t:
                cp.set(c[0], calculate_new_ball_angle_collision_horizontal_bar(self.ball.angle), c[2], HitObject.wall)
        # left wall
        if self.ball.going_left():
            c = moving_circle_to_vertical_bar(position_px, radius_px, a, 0, [0, self.screen_size[1]], start_t)
            if c[0] < cp.t:
                cp.set(c[0], calculate_new_ball_angle_collision_vertical_bar(self.ball.angle), c[2], HitObject.wall)
        # right wall
        if self.ball.going_right():
            c = moving_circle_to_vertical_bar(position_px, radius_px, a, self.screen_size[0], [0, self.screen_size[1]], start_t)
            if c[0] < cp.t:
                cp.set(c[0], calculate_new_ball_angle_collision_vertical_bar(self.ball.angle), c[2], HitObject.wall)

    def brick_type_index(self,key):
        if key == '0' or key == 0:
            bid = 0
        else:
            indices = [i for i, x in enumerate(self.brick_types) if x is not None and key == x.key_in_file]
            if indices:
                bid = indices[0]
            else:
                bid = -1
        return bid

    def tile_to_pixels_rectangle(self,t):
        ret= [int(self.tiles_to_pixels_x(t[0])), int(self.tiles_to_pixels_y(t[1])),
              int(self.tiles_to_pixels_x(t[0]+1))-int(self.tiles_to_pixels_x(t[0])),
              int(self.tiles_to_pixels_y(t[1]+1))-int(self.tiles_to_pixels_y(t[1]))]
        return(ret)
        #return [self.tiles_to_pixels_x(t[0]), self.tiles_to_pixels_y(t[1]), self.tiles_to_pixels_x(1.0), self.tiles_to_pixels_y(1.0)]

    def tiles_to_pixels(self, t):
        return np.array([self.tiles_to_pixels_x(t[0]), self.tiles_to_pixels_y(t[1])])

    def tiles_to_pixels_x(self, tx):
        return (float(tx) / float(self.tiles[0])) * self.screen_size[0]

    def tiles_to_pixels_y(self, ty):
        return (float(ty) / float(self.tiles[1])) * self.screen_size[1]

    def pixels_to_tiles(self, p):
        return [self.pixels_to_tiles_x(p[0]), self.pixels_to_tiles_y(p[1])]

    def pixels_to_tiles_x(self, x):
        return (float(x) / float(self.screen_size[0])) * float(self.tiles[0])

    def pixels_to_tiles_y(self, y):
        return (float(y) / float(self.screen_size[1])) * float(self.tiles[1])

    def horizontal_tiles_to_vertical_tiles(self,tx):
        return (float(tx) / float(self.tiles[0])) * self.tiles[1]
