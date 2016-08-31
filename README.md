# Arkanoid

Python implementation of classic game Arkanoid.

# Dependencies

The game is known to work with

* Python 2.7.6
* pygame 1.9.1
* numpy 1.8.2

Other versions may work too (and probably will) but they are not tested.

# Usage

To start the game run

`python main.py level`

To get a list of available levels simply run the game without specifying the level, i.e.

`python main.py`

Levels are *.lvl files in `levels` subdirectory but to run the game, they must be given without their lvl extension.
When the level is loaded, the board can be freely moved by mouse and the game is started (the ball starts to move)
by clicking anywhere into the window. The game can be further controled by the following keys:

* **n**: Restart the game
* **Esc**: Quit
* **p**: Pause/resume

The game ends if no more bricks can be destroyed or if the ball falls below the upper edge of the board.

### Score

Number of points the player gets for hitting a brick is defined in the source lvl file.
However there is an additional bonus that increases by 1 for every hit brick, that is destroyed
or transformed into another brick. The bonus is reset by hitting the board and if the ball does not 
destroy or transform any brick before it hits the board again, it is decreased by 1. Therefore to 
maximize the score try to keep the ball bouncing from one brick to another as long as possible!


# Levels

Levels are defined in text files with lvl extension in `levels` subdirectory. They set some global properties,
define bricks types and actions to be executed, when a brick is hit, and define layout of the bricks.

### Global properties

Every statement is in simple `key=value` format and must be on a single line.

* `screen.size=(width,height)`  
Sets the window size to width×height pixels.
* `tiles=(width,height)`  
Divide the window into width×height logical cells, where each cell represents one brick.
* `background.color=(r,g,b)`  
Background color of the window.
* `score.color=(r,g,b)`  
Color of the score indicator in the right top corner of the window. The same color is also use to render Victory or Defeat at the end of the game.
* `board.length=f`  
Length of the board (positive number). Units are horizontal tiles (f=1.0 means, that the board will be as wide as one brick).
* `board.color=(r,g,b)`  
Color of the board.
* `ball.radius=f`  
Radius of the ball (positive number). Units are horizontal tiles (f=1.0 means, that the diameter of the ball will be the same as width of two bricks).
* `ball.color=(r,g,b)`  
Color of the ball.
* `ball.initial_speed=f`  
Speed of the ball in horizontal tiles per second.

### Brick types

Levels may contain several types of bricks. Each type has its own set of commands, that are executed
when a brick is hit by a ball or a hit is induced by another command. In order to allow basic `if-then-else`
structure it is possible to condition the execution of each command on the type of the hit. For example
the ball generates hits of type 0 and executes only those commands that are conditioned on type 0.
Commands are executed one after another in the same order as they are specified. 
General syntax for adding a new type of brick is

`add_brick_type(i,(r,g,b),command1,command2,...)`  
* `i`: ID of the brick type (a positive integer). 0 is reserved for the empty space and cannot be used.
* `(r,g,b)`: Color of the brick.
* `commands`: (optional) Actions, that are executed, when the brick is hit by the ball or a hit is induced by another command.
Each command is one of the following:
   * `add_points(n,execute_if_events=(0))`: Add n points to the score.
        * `n`: Number of points.
        * `execute_if_events`: (optional) List of hit types this command is conditioned on. If this parameter is missing, the default value is (0).
   * `add_to_bonus(n,execute_if_events=(0))`: Add n points to the current score bonus.
        * `n`: Number of points.
        * `execute_if_events`: (optional) List of hit types this command is conditioned on. If this parameter is missing, the default value is (0).
    * `delay(ms,execute_if_events=(0))`: Delay execution of the following commands by `ms` milliseconds.
        * `ms`: Delay in milliseconds.
        * `execute_if_events`: (optional) List of hit types this command is conditioned on. If this parameter is missing, the default value is (0).
    * `change_type(type,execute_if_events=(0))`: Change the type of this brick to `type`.
        * `type`: New type of the brick. It must be either an ID defined by another `add_brick_type` or 0, which indicates destruction of the brick.
        * `execute_if_events`: (optional) List of hit types this command is conditioned on. If this parameter is missing, the default value is (0).
    * `destroy(execute_if_events=(0))`: Destroy the brick. Equivalent to `change_type(0,execute_if_events)`.
        * `execute_if_events`: (optional) List of hit types this command is conditioned on. If this parameter is missing, the default value is (0).
    * `hit(dx,dy,generate_events=(0),execute_if_events=(0))`: Invoke hit of another brick.
        * `dx`: Relative horizontal coordinate of the hit brick (0 is the same column).
        * `dy`: Relative vertical coordinate of the hit brick (0 is the same row).
        * `generate_events`: (optional) List of hit types, that are generated by this command. If this parameter is missing, the default value is (0).
        * `execute_if_events`: (optional) List of hit types this command is conditioned on. If this parameter is missing, the default value is (0).
        
Every `add_brick_type` must be completely on a single line.

### Bricks layout

The actual layout of the level comes after all global properties are set and brick types defined. It starts
by a label `bricks:` (which must be on a single line) followed by comma separated table of brick ids
defined by `add_brick_type` (or 0 for empty space). Number of columns must be the same as number of horizontal 
tiles. Rows (each row must be on a single line) are specified from the top edge of the window to the bottom edge
and their number might be arbitrary as missing rows are simply fill by empty space.

The game ends (player wins) if all bricks have been destroyed or no remaining brick has `destroy` or
`change_type` among its commands. The game engine however does not check, whether these commands can
be executed or whether they lead to some final state, that fulfils conditions for the end of the game.
Therefore be kind to the players and make sure, that your levels can be won.

### Comments

In general comments are not allowed in lvl files. However as the values of global properties are interpreted
as Python expressions it is possible to append a Python style comment (starting with #) to them and the
value will be still parsed correctly.

### Example

This level can be found in `levels/house.lvl`. When hit by the ball, brick 1 (black) transforms itself into
brick 2 (blue), which then iteratively transforms itself to brick type 3 (green) and back. The only way, how to destroy
this brick is to hit it when it is green. Brick 4 (red) is a simple type of brick, that is destroyed by the ball with no additional side effects.
Brick 5 (gray) generates hits to its neighbours, which leads to a chain reaction. It also demonstrates how to generate a hit of multiple types.
Brick 6 (brown) demonstrates, how to condition commands on multiple hit types. Brick 7 (light brown) is an example
of a brick with no commands.

```
screen.size=(640,480)
tiles=(11,16)
background.color=(255,255,255)
score.color=(0,0,0)
board.length=2 # units are horizontal tiles
board.color=(64,64,64)
ball.radius=0.15 # units are horizontal tiles
ball.color=(255,0,0) 
ball.initial_speed=6 # units are horizontal tiles per second
add_brick_type(1, (0,0,0), change_type(2), delay(100), hit(0,0,(1)))
add_brick_type(2, (0,0,255), change_type(3,(1)), add_to_bonus(-1,(1)), delay(200,(1)), hit(0,0,(1),(1)))
add_brick_type(3, (0,255,0), change_type(2,(1)), add_to_bonus(-1,(1)), delay(200,(1)), hit(0,0,(1),(1)), add_points(10,(0)), destroy((0)))
add_brick_type(4, (255,0,0), add_points(20), destroy())
add_brick_type(5, (127,127,127), add_points(5), destroy(), delay(100), hit(-1,0,(0,2)), hit(1,0,(0,2)), hit(0,-1,(0,2)), hit(0,1,(0,2)))
add_brick_type(6, (127,63,0), add_points(30,(0,2)), destroy((0,2)))
add_brick_type(7, (190,95,0))
bricks:
0,0,0,0,0,4,0,0,0,0,0
0,0,0,0,4,4,4,0,0,0,0
0,0,0,4,4,4,4,4,0,0,0
0,0,4,4,4,4,4,4,4,0,0
0,1,1,1,1,1,1,1,1,1,0
0,1,5,5,5,5,5,5,5,1,0
0,1,5,6,6,6,6,6,5,1,0
0,1,5,6,6,7,6,6,5,1,0
0,1,5,6,6,6,6,6,5,1,0
0,1,1,1,1,1,1,1,1,1,0
```
