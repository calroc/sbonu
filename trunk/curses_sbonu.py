import curses

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
