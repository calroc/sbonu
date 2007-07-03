#!/usr/bin/env python
import curses
from time import sleep
from sbonu import DIMENSION, setup_sim
from space import _calories

# Initialize curses
_stdscr = curses.initscr()
curses.start_color()
curses.noecho()
curses.cbreak()
curses.curs_set(0)
_stdscr.keypad(1)
_stdscr.nodelay(1)

# Initialize a bunch of colour pairs.
BLACK_BLACK = 1
RED_BLACK = 2
GREEN_BLACK = 3
BLUE_BLACK = 4
curses.init_pair(BLACK_BLACK, curses.COLOR_BLACK, curses.COLOR_BLACK)
curses.init_pair(RED_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(GREEN_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(BLUE_BLACK, curses.COLOR_BLUE, curses.COLOR_BLACK)


def spaceToPad(space, pad):
    for y in range(space.dim):
        pad.move(y, 0)
        pad.clrtoeol()
        for x in range(space.dim):
            L = space.get(x,y)
            if L:
                pad.addstr(y, x, str(L), colour(L))


def colour(location):
    '''
    Return a color_pair (possibly with attribute).
    '''
    n = len(location.occupants)
    if n:
        if n == 1:
            occ = location.occupants[0]
            if occ.infections:
                return curses.color_pair(RED_BLACK)
            else:
                return curses.color_pair(BLUE_BLACK)
        elif n > 9:
            return curses.color_pair(BLUE_BLACK)
        else:
            return curses.color_pair(BLUE_BLACK)
    elif location.food:
        return curses.color_pair(GREEN_BLACK)
    return curses.color_pair(BLACK_BLACK) | curses.A_BOLD


pad = curses.newpad(DIMENSION + 1, DIMENSION + 1)


def onestep(generations, sim, display_y, display_x):
    sim.step()

    pop, infected, immune = sim.space.getStats()

    if infected < 0.008:
        return 'break'

##    print '%s %.02f %.02f %05i %-3i %i' % (str(s), infected, immune, n, int(_N), Alice.foods)

    spaceToPad(sim.space, pad)
    status = '%.02f %.02f %05i %-i' % (infected, immune, generations, int(pop))
##    _stdscr.addstr(DIMENSION - 1, DIMENSION, status)

    Y, X = _stdscr.getmaxyx()
    pad.refresh(display_y, display_x,  0, 0,  Y-1, X-1)

##    print '%s %.02f %.02f %05i %-i' % (str(s), infected, immune, n,
##                                       int(_N))
##    print '%.02f %.02f %05i %-i' % (infected, immune, n, int(_N))

##    row = (n, infected, immune, _N, fud)
##    w.writerow(row)

    if infected + immune == 1:
        return 'break'
##    print ' '.join('%04i' % (npc.foods,) for npc in NPCs)


def deinit_curses():
    global _stdscr
    _stdscr.clear();
    _stdscr.move(0,0);
    curses.nocbreak()
    _stdscr.keypad(0)
    curses.curs_set(1)
    curses.echo()
    curses.endwin()


def main():

    Alice, spawner, sim = setup_sim()

    step_delay = 1.0/23

    # Top left coordinates of section of space displayed.
    display_x = 0
    display_y = 0

    try:
        for n in range(10000):
            if onestep(n, sim, display_y, display_x):
                break
            else:
                key = _stdscr.getch()
                if (key == ord('q')) or (key == ord('Q')):
                    break
                elif key == ord('+'):
                    step_delay *= 0.5
                elif key == ord('-'):
                    step_delay *= 1.5
                elif key == curses.KEY_DOWN:
                    Y, X = _stdscr.getmaxyx()
                    if DIMENSION - display_y > Y:
                        display_y += 1
                elif key == curses.KEY_UP:
                    if display_y > 0:
                        display_y -= 1
                elif key == curses.KEY_RIGHT:
                    Y, X = _stdscr.getmaxyx()
                    if DIMENSION - display_x > X:
                        display_x += 1
                elif key == curses.KEY_LEFT:
                    if display_x > 0:
                        display_x -= 1
                sleep(step_delay)

    finally:
        deinit_curses()

    folks = list(sim.space.yieldPeople())
    foods = sum(npc.foods for npc in folks)
    pop = len(folks)

    print 'Virulence:', spawner.spore_class.virulence
    print 'Initial Population:', 60
    print 'Eventual Population:', pop
    print 'Iterations:', n + 1
    print 'Dimensions: %i x %i' % (DIMENSION, DIMENSION)
    print 'Total calories:', _calories
    print 'Average stored: %.01f' % (foods / pop,)

if __name__ == '__main__':
    main()

