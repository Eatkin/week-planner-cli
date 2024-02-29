import curses

# Define some colours with colours pair

# Define a class to hold the colours
class Colours:
    def __init__(self):
        # Initialise the colours
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_RED)

        # Dictionary to hold the colours
        self.colours = {
            "black": 1,
            "white": 2,
            "red": 3,
            "green": 4,
            "blue": 5,
            "yellow": 6,
            "cyan": 7,
            "magenta": 8,
            "highlight": 9,
            "highlight_red": 10
        }

    def get_colour(self, colour):
        return curses.color_pair(self.colours[colour])
