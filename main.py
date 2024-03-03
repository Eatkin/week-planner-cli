import calendar
import random
import curses
import atexit
import logging
import os
from time import sleep
from datetime import datetime
from components import Container, Label, Combobox, Button
from activity import Activity, read_activities, write_activities
from states import StateMain


# Set up logging
if not os.path.exists('logs'):
    os.makedirs('logs')
logging.basicConfig(filename=f'logs/week_planner_{datetime.now()}.log', level=logging.DEBUG)

# Register exit function to clean up curses
@atexit.register
def cleanup():
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    curses.curs_set(0)


def main():
    try:
        # Instantiate the main state
        state = StateMain(stdscr)

        # Main loop
        while True:
            # Set curses x/y to 0
            stdscr.move(0, 0)
            c = stdscr.getch()
            state.handle_input(c)
            state_change = state.update()
            state.render()
            if c == ord('q'):
                break

            if state_change:
                state = state_change
                stdscr.clear()

            stdscr.refresh()

    except Exception as e:
        logging.exception(e)




if __name__ == "__main__":
    # Initialise curses
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(1)
    curses.curs_set(0)

    main()
