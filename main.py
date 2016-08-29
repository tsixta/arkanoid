import pygame
import sys
from level import Level
from os.path import splitext, dirname, realpath


if len(sys.argv)<2:
    from glob import glob
    import ntpath
    print 'Usage:'
    print 'python main.py level'
    print ''
    print 'Available levels are:'
    levels = glob(dirname(realpath(__file__))+'/levels/*.lvl')
    for level in levels:
        print splitext(ntpath.basename(level))[0]
else:
    pygame.init()
    pygame.display.set_caption('Arkanoid level '+sys.argv[1])
    clock = pygame.time.Clock()
    filename = dirname(realpath(__file__)) + '/levels/'+sys.argv[1]+'.lvl'
    l = Level()
    l.load(filename)
    screen = pygame.display.set_mode(l.screen_size)
    board_position = l.initialize(pygame,screen)
    pygame.display.update()
    quit_game = False
    was_p_pressed = False
    was_n_pressed = False
    while True:
        if pygame.key.get_pressed()[27]:
            quit_game = True
        if was_n_pressed and not pygame.key.get_pressed()[78] and not pygame.key.get_pressed()[110]:
            l = Level()
            l.load(filename)
            board_position = l.initialize(pygame, screen)
            pygame.display.update()
            l.paused = False
            was_n_pressed = False
        if l.game_started and was_p_pressed and not pygame.key.get_pressed()[80] and not pygame.key.get_pressed()[112]:
            l.paused = not l.paused or l.defeated or l.won
            was_p_pressed = False
        was_p_pressed = l.game_started and pygame.key.get_pressed()[80] or pygame.key.get_pressed()[112]
        was_n_pressed = l.game_started and pygame.key.get_pressed()[78] or pygame.key.get_pressed()[110]
        if pygame.mouse.get_pressed()[0]:
            l.start_game()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game = True
            elif event.type == pygame.MOUSEMOTION:
                board_position = event.pos[0]
        if quit_game is True:
            break
        msElapsed = clock.tick(200) # the parameter is desired framerate
        rectangles = l.redraw(pygame,screen,board_position,float(msElapsed)/1000.0)
        pygame.display.update(rectangles)

    pygame.quit()
    sys.exit()
