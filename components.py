"""UI components for the application"""
import curses
import logging
import random
from colours import Colours
from activity import read_activities

class Component:
    def __init__(self):
        """Sets basic properties of a component"""
        self.selectable = False
        self.selected = False

    def update(self):
        """Update the component"""
        pass

    def handle_input(self, key):
        """Handle input for the component"""
        pass

class Container(Component):
    """A simple container for other UI components"""
    def __init__(self, stdscr):
        """Initialise the container with a list of components"""
        super().__init__()
        self.stdscr = stdscr
        self.components = []
        # Set container boundaries
        # self.bbox_left = 0
        # self.bbox_right = 0
        # self.bbox_top = 0
        # self.bbox_bottom = 0

    def handle_input(self, key):
        """This will determine up/down navigation between components in the container and update the component accordingly"""
        if key == -1:
            return
        v_movement = 0
        if key == curses.KEY_DOWN:
            v_movement = 1
        elif key == curses.KEY_UP:
            v_movement = -1

        # Find the next selectable component and select it (wrapping around if necessary)
        for i, component in enumerate(self.components):
            if component.selected:
                component.selected = False
                while self.components[(i + v_movement) % len(self.components)].selectable == False:
                    v_movement += v_movement // abs(v_movement)
                self.components[(i + v_movement) % len(self.components)].selected = True
                break

        # Handle input for the selected component
        for component in self.components:
            if component.selected:
                component.handle_input(key)



    def update(self):
        """Update all the components in the container if they are selected"""
        for component in self.components:
            if component.selected:
                component.update()

    def render(self):
        """Render all the components in the container"""
        for component in self.components:
            component.render()
            self.stdscr.addstr("\n")

    def add_component(self, component, args=()):
        """Add a component to the container"""
        # Create the component by unpacking the args and adding stdscr and container
        self.components.append(component(*args, self.stdscr, self))
        # If this is the first component that is selectable then select it
        if self.components[-1].selectable and not any(c.selected for c in self.components):
            self.components[-1].selected = True

class Label(Component):
    """A simple label to display text"""
    def __init__(self, text, stdscr, container):
        """Initialise the label with some text and a curses window"""
        super().__init__()
        self.selectable = False
        self.text = text
        self.stdscr = stdscr
        self.container = container
        # Create colour object
        self.colours = Colours()

    def render(self):
        """Render the label to the curses window"""
        _, t_width = self.stdscr.getmaxyx()
        padding = (t_width - len(self.text) - 2) // 2
        self.stdscr.addstr(" " * padding)
        self.stdscr.addstr(f"⌡{self.text}⌠", self.colours.get_colour("green"))

class Combobox(Component):
    """A simple combo box allowing left/right navigation to select an item"""
    def __init__(self, items, stdscr, container):
        """Initialise the combo box with a list of items and a curses window"""
        super().__init__()
        self.selectable = True
        self.selected = False
        self.items = items
        self.index = 0
        self.stdscr = stdscr
        # Create colour object
        self.colours = Colours()

    def handle_input(self, key):
        """Handle input for the combo box, moving left/right to select an item"""
        if key == -1:
            return
        if key == curses.KEY_LEFT:
            self.index = max(0, self.index - 1)
        elif key == curses.KEY_RIGHT:
            self.index = min(len(self.items) - 1, self.index + 1)

    def render(self):
        """Render the combo box to the curses window with left/right arrows around the selected item"""
        # Highlight in white if selected
        col = self.colours.get_colour("black")
        if self.selected:
            col = self.colours.get_colour("white")

        _, t_width = self.stdscr.getmaxyx()
        if self.index > 0 or self.index < len(self.items) - 1:
            t_width -= 1
        padding = (t_width - len(self.value) - 2) // 2
        self.stdscr.addstr(" " * padding)

        # Draw the selection with arrows
        if self.index > 0:
            self.stdscr.addstr("◄", col | curses.A_BOLD)
        self.stdscr.addstr(f" {self.value} ", col)
        if self.index < len(self.items) - 1:
            self.stdscr.addstr("►", col | curses.A_BOLD)

    @property
    def value(self):
        return self.items[self.index]

class Button(Component):
    """A simple button to perform an action when selected"""
    def __init__(self, text, action, stdscr, container):
        """Initialise the button with some text and a curses window"""
        super().__init__()
        self.selectable = True
        self.selected = False
        self.text = text
        self.stdscr = stdscr
        self.container = container
        self.action = action
        # Create colour object
        self.colours = Colours()

    def handle_input(self, key):
        """Handle input for the button, performing the action when selected"""
        if key == -1:
            return
        if key == ord("\n"):
            logging.info(f"Button pressed: {self.text}")
            self.action()
            # Clear input buffer
            curses.flushinp()

    def update(self):
        """Perform the action when key is pressed and button is selected"""
        pass

    def render(self):
        """Render the button to the curses window"""
        col = self.colours.get_colour("black")
        if self.selected:
            col = self.colours.get_colour("highlight")
            if self.text == "Quit":
                col = self.colours.get_colour("highlight_red")

        _, t_width = self.stdscr.getmaxyx()
        padding = (t_width - len(self.text) - 1) // 2
        self.stdscr.addstr(" " * padding)
        self.stdscr.addstr(f"[{self.text}]", col)
