# Arkanoid

Python implementation of classic game Arkanoid.

# Configurations known to work

* Python 2.7.6
* pygame 1.9.1
* numpy 1.8.2

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


# Level files

Levels are defined in text files with lvl extension in `levels` subdirectory. 

