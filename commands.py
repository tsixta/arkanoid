#from enum import Enum


class CommandTypes():
    noop = 0
    destroy = 1
    change_brick_type = 2
    delay = 3
    hit_brick = 4
    add_points = 5

class Command:
    type = CommandTypes.noop
    parameters = ()
    timestamp = -1.0

    def __init__(self, command_type, parameters, timestamp):
        self.type = command_type
        self.parameters = parameters
        self.timestamp = timestamp

    def __str__(self):
        return 'c[type='+str(self.type)+', parameters='+str(self.parameters)+', timestamp='+str(self.timestamp)+']'

    def __repr__(self):
        return self.__str__()


def parse_line(line):
    command = ''
    arguments = ''
    line = line.replace('(', '[')
    line = line.replace(')', ']')
    if line[-1] == ':':
        command = (line[:-1]).strip()
    else:
        eq_pos = line.find('=')
        if eq_pos > -1:
            command = (line[:eq_pos]).strip()
            arguments = (line[eq_pos + 1:]).strip()
        else:
            par_pos = line.find('[')
            command = (line[:par_pos]).strip()
            arguments = (line[par_pos:]).strip()
    return command, arguments


def nail_down_command(arguments, command):
    start = arguments.find(command)
    end = -1
    if start >= 0:
        end = arguments.find('[', start)
    return start, end


def preprocess_brick_type(arguments):
    command_replaced = True
    ret = arguments
    while command_replaced:
        command_replaced = False
        pos, end_pos = nail_down_command(ret, 'noop')
        if pos >= 0 and end_pos >= 0:
            needle = ret[pos:end_pos+1]
            ret = ret.replace(needle, '['+str(int(CommandTypes.noop))+',')
            command_replaced = True
        pos, end_pos = nail_down_command(ret, 'destroy')
        if pos >= 0 and end_pos >= 0:
            needle = ret[pos:end_pos + 1]
            ret = ret.replace(needle, '['+str(int(CommandTypes.destroy))+',')
            command_replaced = True
        pos, end_pos = nail_down_command(ret, 'change_type')
        if pos >= 0 and end_pos >= 0:
            needle = ret[pos:end_pos + 1]
            ret = ret.replace(needle, '['+str(int(CommandTypes.change_brick_type))+',')
            command_replaced = True
        pos, end_pos = nail_down_command(ret, 'delay')
        if pos >= 0 and end_pos >= 0:
            needle = ret[pos:end_pos + 1]
            ret = ret.replace(needle, '['+str(int(CommandTypes.delay))+',')
            command_replaced = True
        pos, end_pos = nail_down_command(ret, 'hit')
        if pos >= 0 and end_pos >= 0:
            needle = ret[pos:end_pos + 1]
            ret = ret.replace(needle, '['+str(int(CommandTypes.hit_brick))+',')
            command_replaced = True
        pos, end_pos = nail_down_command(ret, 'add_points')
        if pos >= 0 and end_pos >= 0:
            needle = ret[pos:end_pos + 1]
            ret = ret.replace(needle, '[' + str(int(CommandTypes.add_points)) + ',')
            command_replaced = True
    return ret

def convert_to_set(x):
    if type(x) is tuple or type(x) is list:
        return set(x)
    else:
        return set([x])
    

