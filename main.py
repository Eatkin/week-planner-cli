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

# Globals
filename = 'activities.txt'

# Initialise curses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)

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


def main():
    try:
        container = Container(stdscr)
        container.add_component(Label, ["Welcome to Week Planner!"])

        # Get activities so we can make comboboxes for them
        activities = read_activities(filename)

        activity_labels = [activity.get_activity() for activity in activities]

        logging.debug(f"Activities: {activity_labels}")

        # Create a combobox for each day of the week
        for day in calendar.day_name:
            container.add_component(Label, [day])
            container.add_component(Combobox, [activity_labels])

        # Main loop
        while True:
            stdscr.clear()
            container.update()
            container.render()
            stdscr.refresh()
            c = stdscr.getch()
            if c == ord('q'):
                break

            # Sleep to avoid flickering
            sleep(0.1)
    except Exception as e:
        logging.exception(e)




if __name__ == "__main__":
    main()
