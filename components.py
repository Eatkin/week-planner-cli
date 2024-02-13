"""UI components for the application"""
import curses
import logging
from colours import Colours

class Container:
    """A simple container for other UI components"""
    def __init__(self, stdscr):
        """Initialise the container with a list of components"""
        self.stdscr = stdscr
        self.components = []
        # Set container boundaries
        self.bbox_left = 0
        self.bbox_right = 0
        self.bbox_top = 0
        self.bbox_bottom = 0

    def update(self):
        """This will determine up/down navigation between components in the container and update the component accordingly"""
        pass

    def render(self):
        """Render all the components in the container"""
        for component in self.components:
            component.render()
            self.stdscr.addstr("\n")

    def add_component(self, component, args=()):
        """Add a component to the container"""
        # Create the component by unpacking the args and adding stdscr and container
        self.components.append(component(*args, self.stdscr, self))

class Label:
    """A simple label to display text"""
    def __init__(self, text, stdscr, container):
        """Initialise the label with some text and a curses window"""
        self.selectable = False
        self.text = text
        self.stdscr = stdscr
        self.container = container
        # Create colour object
        self.colours = Colours()

    def render(self):
        """Render the label to the curses window"""
        self.stdscr.addstr(f"⌡{self.text}⌠", self.colours.get_colour("white"))

class Combobox:
    """A simple combo box allowing left/right navigation to select an item"""
    def __init__(self, items, stdscr, container):
        """Initialise the combo box with a list of items and a curses window"""
        self.selectable = True
        self.selected = False
        self.items = items
        self.index = 0
        self.stdscr = stdscr
        # Create colour object
        self.colours = Colours()

    def render(self):
        """Render the combo box to the curses window with left/right arrows around the selected item"""
        # Highlight in white if selected
        col = self.colours.get_colour("black")
        if self.selected:
            col = self.colours.get_colour("white")

        # Draw the selection with arrows
        if self.index > 0:
            self.stdscr.addstr("◄", col | curses.A_BOLD)
        self.stdscr.addstr(f" {self.value} ", col)
        if self.index < len(self.items) - 1:
            self.stdscr.addstr("►", col | curses.A_BOLD)

    @property
    def value(self):
        return self.items[self.index]

class Button:
    """A simple button to perform an action when selected"""
    def __init__(self, text, action, stdscr, container):
        """Initialise the button with some text and a curses window"""
        self.selectable = True
        self.selected = False
        self.text = text
        self.stdscr = stdscr
        self.container = container
        self.action = action
        # Create colour object
        self.colours = Colours()

    def update(self):
        """Perform the action when key is pressed and button is selected"""
        pass

    def render(self):
        """Render the button to the curses window"""
        self.stdscr.addstr(f"[{self.text}]", self.colours.get_colour("white"))
