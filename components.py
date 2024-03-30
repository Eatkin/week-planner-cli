"""UI components for the application"""
import curses
import curses.ascii
import logging
from math import floor
from colours import Colours
from utils import clamp

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

    def on_select(self):
        """Perform an action when the component is selected"""
        pass

    def on_deselect(self):
        """Perform an action when the component is deselected"""
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
                component.on_deselect()
                while self.components[(i + v_movement) % len(self.components)].selectable == False:
                    v_movement += v_movement // abs(v_movement)
                next_component = self.components[(i + v_movement) % len(self.components)]
                next_component.selected = True
                next_component.on_select()
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

class MenuList():
    """This is the same as menu with different rendering logic"""
    def __init__(self, stdscr, items, functions, menu_title='Menu'):
        # Define the menu items and selection
        self.menu_title = menu_title
        self.items = items
        self.functions = functions
        self.selected = 0

        # Use items to determine the width and height of the menu
        self.width = max([len(item) for item in self.items + [self.menu_title if self.menu_title else ""]]) + 4
        self.height = len(self.items) + 4
        self.h_padding = 4
        self.v_padding = 1
        # Add on the padding
        self.width += self.h_padding

        # Set up colours
        self.colours = Colours()

        # Define scr
        self.stdscr = stdscr

        # Min will be 2 but this will get updated in render
        self.menu_title_height = 2
        self.offset = 0

    def handle_input(self, key):
        """Get keyboard input to navigate the menu,"""
        vinput = 0
        if key == curses.KEY_UP:
            vinput -= 1
        if key == curses.KEY_DOWN:
            vinput += 1

        # Pg up and pg down - move by page_skip
        page_skip = 10
        if key == curses.KEY_PPAGE:
            vinput -= page_skip
            # Make sure we don't go out of bounds
            vinput = clamp(vinput, -self.selected, len(self.items) - 1 - self.selected)
        if key == curses.KEY_NPAGE:
            vinput += page_skip
            # Make sure we don't go out of bounds
            vinput = clamp(vinput, -self.selected, len(self.items) - 1 - self.selected)

        # Home and end - move to start and end
        if key == curses.KEY_HOME:
            vinput = -self.selected
        if key == curses.KEY_END:
            vinput = len(self.items) - 1 - self.selected

        # Escape to invoke the "Back" function if one exists
        # This is slow for some reason
        if key == curses.ascii.ESC:
            if "Back" in self.items:
                # Find the index of the back button
                back_index = self.items.index("Back")
                return self.functions[back_index]

        # Update the selected item
        self.selected += vinput


        # scrolling behaviour
        # First we wrap from first to last item and vice versa if out of bounds
        self.selected = self.wrap(self.selected, 0, len(self.items) - 1)

        # Then we adjust the offset of the menu if we are a scroll type menu (a list style menu)
        self.offset, self.selected = self.scroll(self.offset, self.selected)

        # Check for enter key
        if key == curses.KEY_ENTER or key in [10, 13]:
            # Return the function for the state to call
            return self.functions[self.selected]

        return None

    def render(self):
        """Draw the list of menu items"""
        # Get terminal size
        t_height, t_width = self.stdscr.getmaxyx()

        dy = 0

        # First draw menu title
        if self.menu_title is not None:
            # Get the y pos
            y, x = self.stdscr.getyx()
            # Draw menu title in italic yellow
            col = self.colours.get_colour('yellow')
            xoffset = round((t_width - len(self.menu_title)) * 0.5)
            self.stdscr.addstr(" " * xoffset + self.menu_title, col | curses.A_ITALIC)
            self.stdscr.addstr("\n")
            # Draw a line under the title
            self.stdscr.addstr("." * t_width, col)
            dy = self.stdscr.getyx()[0] - y

            # Update menu title height
            self.menu_title_height = dy

        # Call the scroll function to adjust the scroll if needed
        self.offset, self.selected = self.scroll(self.offset, self.selected)

        # We slice items based on the offset
        items_to_render = self.items[self.offset:self.offset + t_height - dy]
        # Draw the items - this will except if it goes out of bounds
        for index, item in enumerate(items_to_render):
            try:
                col = self.colours.get_colour('black')
                if index + self.offset == self.selected:
                    col = self.colours.get_colour('highlight')

                # Centre the item
                if len(item) < t_width:
                    xoffset = floor((t_width - len(item)) * 0.5)
                    self.stdscr.addstr(" " * xoffset)
                    self.stdscr.addstr(item, col)
                else:
                    try:
                        # We need to do string slicing to get the item to fit
                        # Split string and add one word at a time until we overflow the terminal
                        words = item.split(" ")
                        lines = [""]
                        lines_index = 0
                        for word in words:
                            if len(lines[lines_index]) + len(word) + 1 < t_width:
                                lines[lines_index] += word + " "
                            else:
                                # Cut the last space
                                lines[lines_index] = lines[lines_index][:-1]
                                lines_index += 1
                                lines.append(word + " ")

                        # Now we can draw the lines centred
                        for i, line in enumerate(lines):
                            xoffset = floor((t_width - len(line)) * 0.5)
                            self.stdscr.addstr(" " * xoffset)
                            self.stdscr.addstr(line, col)
                            if i < len(lines) - 1:
                                self.stdscr.addstr("\n")
                    except Exception as e:
                        logging.warning(f"Failed to draw item: {item}")
                        logging.warning(e)
                        break

                try:
                    self.stdscr.addstr("\n")
                except:
                    break
            except Exception as e:
                # In this case we've gone out of bounds so ensure selection is within bounds
                # I don't think this ever happens
                y, _ = self.stdscr.getyx()
                if y > t_height:
                    # This will adjust the scroll if needed
                    if index - self.offset - dy <= self.selected:
                        logging.debug(f"Adjusting scroll up by {y - t_height - dy}")
                        self.offset -= (y - t_height - dy)
                        self.stdscr.clear()
                        self.stdscr.refresh()
                        self.render()
                    break

    def scroll(self, scroll, selection):
        """Scroll a number between min and max"""
        # Adjust scroll if needed
        height, _ = self.stdscr.getmaxyx()

        if selection < scroll:
            scroll = selection
        elif selection >= scroll + height - 1 - self.menu_title_height:
            scroll = selection - height + 1 + self.menu_title_height

        return scroll, selection

    def wrap(self, selection, min, max):
        """Wrap a number between min and max"""
        if selection < min:
            return max
        elif selection > max:
            return min
        else:
            return selection

class TextInput(Component):
    """A simple text input to allow text entry"""
    def __init__(self, stdscr, container):
        """Initialise the text input with a curses window"""
        super().__init__()
        self.selectable = True
        self.selected = False
        self.text = ""
        self.stdscr = stdscr
        self.container = container
        # Create colour object
        self.colours = Colours()

    def handle_input(self, key):
        """Handle input for the text input, adding characters to the text"""
        if key == -1:
            return
        if key == curses.ascii.ESC:
            self.text = ""
        elif key == curses.ascii.BS:
            self.text = self.text[:-1]
        elif key == ord("\n"):
            logging.info(f"Text input: {self.text}")
        elif key < 256:
            self.text += chr(key)

    def render(self):
        """Render the text input to the curses window"""
        col = self.colours.get_colour("black")
        if self.selected:
            col = self.colours.get_colour("highlight")

        # Draw this if selected
        if self.selected:
            prepend = "> "
        else:
            prepend = ""

        _, t_width = self.stdscr.getmaxyx()
        padding = (t_width - len(self.text) - len(prepend) - 1) // 2
        self.stdscr.addstr(" " * padding)
        self.stdscr.addstr(f"{prepend}{self.text}", col)
