import calendar
import curses
import random
import os
import logging
from datetime import datetime

from activity import Activity, read_activities, write_activities
from components import *

state_history = []

class State:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.container = None
        self.next_state = None
        state_history.append(self)

    def update(self):
        if self.next_state:
            regressing = False
            if state_history[-1] == self.next_state:
                regressing = True
            # Store this state so we can clear it
            state = self.next_state
            self.next_state = None

            if regressing:
                state.on_regress()

            return state
        return None

    def handle_input(self, key):
        if self.container:
            self.container.handle_input(key)

    def render(self):
        if self.container:
            self.container.render()

    def advance_state(self, state):
        self.next_state = state

    def regress_state(self):
        state_history.pop()
        self.next_state = state_history[-1]

    def on_regress(self):
        pass

    def get_random_activity(self):
        activities = read_activities('activities.txt')
        # Adjust priorities based on when activities were last recommended
        activities = self.adjust_priorities(activities)

        # Now we make up a list with each activity * priority
        choices = []
        for activity in activities:
            for i in range(activity.priority):
                choices.append(activity.choice)

        return random.choice(choices)

    def adjust_priorities(self, activities):
        """Looks at previous weeks plan and adjusts priorities"""
        plans = os.listdir("plans")
        if len(plans) > 0:
            # Sort by date
            plans.sort(reverse=True)
            all_activities = [activity.get_activity() for activity in activities]
            found_activities = []
            for plan in plans:
                logging.info(f"Reading plan: {plan}")
                with open (f"plans/{plan}", "r") as f:
                    for line in f:
                        activity = line.split(":")[1].strip()
                        if activity in all_activities:
                            found_activities.append(activity)
                            all_activities.remove(activity)

                logging.info(f"Found activities: {found_activities}")
                logging.info(f"Remaining activities: {all_activities}")

                # Increase priority of not found activities
                for activity in activities:
                    if activity.get_activity() not in found_activities:
                        logging.info(f"Increasing priority of {activity.get_activity()}")
                        activity.priority += 1

                # If there's no activities left then break
                if not all_activities:
                    break

        return activities

class StateMain(State):
    def __init__(self, stdscr):
        """Initialise the main state"""
        super().__init__(stdscr)
        self.container = Container(stdscr)
        self.container.add_component(Label, ["Welcome to Week Planner!"])
        # Button/lambda function pairs to add to the container
        buttons = [
            ("Week Planner", lambda: self.advance_state(StateWeekPlanner(stdscr))),
            ("Random Activity", lambda: self.advance_state(StateRandomActivity(stdscr))),
            ("Config", lambda: self.advance_state(StateConfig(stdscr))),
            ("Quit", lambda: exit(1))
        ]
        for b in buttons:
            self.container.add_component(Button, [b[0], b[1]])


class StateWeekPlanner(State):
    def __init__(self, stdscr):
        """Initialise the main state"""
        super().__init__(stdscr)
        self.container = Container(stdscr)
        self.container.add_component(Label, ["Welcome to Week Planner!"])

        filename = 'activities.txt'

        # Get activities so we can make comboboxes for them
        activities = read_activities(filename)

        activity_labels = [activity.get_activity() for activity in activities]

        # Create a combobox for each day of the week
        for day in calendar.day_name:
            self.container.add_component(Label, [day])
            self.container.add_component(Combobox, [activity_labels])

        # Add a generate button
        self.container.add_component(Button, ["Randomise!", lambda: self.randomise_activities()])
        self.container.add_component(Button, ["Export Plan", lambda: self.export_plan()])
        self.container.add_component(Button, ["Back", lambda: self.regress_state()])

    def randomise_activities(self):
        """Randomise the activities in the comboboxes"""
        # Get our containers components
        components = self.container.components

        for component in components:
            if isinstance(component, Combobox):
                choice = self.get_random_activity()
                component.index = component.items.index(choice)

    def export_plan(self):
        """Export the plan to a file with the current date as the filename"""
        components = self.container.components
        plan = ""
        days = [day for day in calendar.day_name]
        days = iter(days)
        day = next(days)
        for component in components:
            if isinstance(component, Combobox):
                plan += f"{day}: {component.items[component.index]}\n"
                try:
                    day = next(days)
                except:
                    pass

        # Write plan to file with current date
        filename = f"week_plan_{datetime.now().strftime('%Y-%m-%d')}.txt"

        if not os.path.isdir("plans"):
            os.mkdir("plans")

        with open(f"plans/{filename}", "w") as f:
            f.write(plan)

class StateRandomActivity(State):
    def __init__(self, stdscr):
        """Initialise the main state"""
        super().__init__(stdscr)
        self.container = Container(stdscr)
        self.container.add_component(Label, ["Welcome to Random Activity!"])
        self.container.add_component(Label, [f"Your random activity is: {self.get_random_activity()}"])
        self.container.add_component(Button, ["I don't want to do that", lambda: self.reroll_activity()])
        self.container.add_component(Button, ["Back", lambda: self.regress_state()])

    def reroll_activity(self):
        """Rerolls the activity"""
        self.container.components[1].text = f"Your random activity is: {self.get_random_activity()}"


class StateConfig(State):
    def __init__(self, stdscr):
        """Initialise the main state"""
        super().__init__(stdscr)
        self.container = Container(stdscr)
        self.container.add_component(Label, ["Welcome to Config!"])
        # New activity
        self.container.add_component(Button, ["New Activity", lambda: self.advance_state(StateNewActivity(stdscr))])
        # Edit activities button
        self.container.add_component(Button, ["Edit Activities", lambda: self.advance_state(StateEditActivities(stdscr))])
        # And a week config button
        self.container.add_component(Button, ["Week Config", lambda: self.advance_state(StateWeekConfig(stdscr))])
        self.container.add_component(Button, ["Back", lambda: self.regress_state()])

class StateEditActivities(State):
    def __init__(self, stdscr):
        """Initialise the edit activities state"""
        super().__init__(stdscr)
        # We use a list menu to display the activities here
        # So we need a list of activities
        self.create_list_menu()

    def handle_input(self, key):
        callback = self.list_menu.handle_input(key)
        if callback:
            callback()

    def render(self):
        self.list_menu.render()

    def create_list_menu(self):
        activities = read_activities('activities.txt')
        activities = [activity.get_activity() for activity in activities]
        functions = [lambda activity=activity: self.advance_state(StateEditActivity(self.stdscr, activity)) for activity in activities]
        # Add a back button
        activities.append("Back")
        functions.append(lambda: self.regress_state())
        # Now make the list menu
        self.list_menu = MenuList(self.stdscr, activities, functions, "Welcome to Edit Activities!")

    def update_list_menu(self):
        # Similar to above but overwrite the functions and activities for the menu
        activities = read_activities('activities.txt')
        activities = [activity.get_activity() for activity in activities]
        functions = [lambda activity=activity: self.advance_state(StateEditActivity(self.stdscr, activity)) for activity in activities]
        # Add a back button
        activities.append("Back")
        functions.append(lambda: self.regress_state())

        self.list_menu.functions = functions
        self.list_menu.items = activities

        if self.list_menu.selected > 0:
            self.list_menu.selected -= 1


    def on_regress(self):
        """Refresh the list of functions"""
        self.update_list_menu()



class StateWeekConfig(State):
    def __init__(self, stdscr):
        """Initialise the main state"""
        super().__init__(stdscr)
        self.container = Container(stdscr)
        self.container.add_component(Label, ["Welcome to Week Config!"])
        self.container.add_component(Label, ["Coming soon! (Probably not actually I cba lol)"])
        self.container.add_component(Button, ["Back", lambda: self.regress_state()])

class StateEditActivity(State):
    def __init__(self, stdscr, activity):
        """Initialise the main state"""
        super().__init__(stdscr)
        # Get all the activities
        logging.info(f"Activity to edit: {activity}")
        self.activities = read_activities('activities.txt')
        # Find our priority
        for a in self.activities:
            if a.get_activity() == activity:
                priority = a.priority
                break
        self.activity = activity
        self.container = Container(stdscr)
        self.container.add_component(Label, ["Welcome to Edit Activity!"])
        self.container.add_component(Label, [f"Editing activity: {activity}"])
        self.container.add_component(Combobox, [["Ignore", "Low", "Medium", "High", "Very High", "Ultra High", "Mega High", "Giga High", "Tera High", "Peta High", "Exa High"]])
        # Set the index of the combobox to the priority
        self.container.components[-1].index = priority
        # Add a delete activity button
        self.container.add_component(Button, ["Delete Activity", lambda: self.delete_activity()])
        # Add a save button
        self.container.add_component(Button, ["Save", lambda: self.save_activity()])
        self.container.add_component(Button, ["Back", lambda: self.regress_state()])

    def delete_activity(self):
        """Removes acitivty from activities.txt"""
        # Loop over activities and remove the one we want
        for a in self.activities:
            if a.get_activity() == self.activity:
                self.activities.remove(a)
                break

        # Write activities back to file
        write_activities('activities.txt', self.activities)

        # Then regress the state - why doesn't this work?
        self.regress_state()

    def save_activity(self):
        """Alter the priority of the activity"""
        for a in self.activities:
            if a.get_activity() == self.activity:
                a.priority = self.container.components[2].index
                break

        # Write activities back to file
        write_activities('activities.txt', self.activities)

class StateNewActivity(State):
    def __init__(self, stdscr):
        """Initialise the new activity state"""
        super().__init__(stdscr)
        self.container = Container(stdscr)
        self.container.add_component(Label, ["Welcome to New Activity!"])
        self.container.add_component(Label, ["Enter the name of the new activity:"])
        self.container.add_component(TextInput, [])
        self.container.add_component(Label, ["Enter the priority of the new activity:"])
        self.container.add_component(Combobox, [["Ignore", "Low", "Medium", "High", "Very High", "Ultra High", "Mega High", "Giga High", "Tera High", "Peta High", "Exa High"]])
        self.container.add_component(Button, ["Create Activity", lambda: self.create_activity()])
        self.container.add_component(Button, ["Back", lambda: self.regress_state()])

    def create_activity(self):
        """Creates a new activity and adds it to activities.txt"""
        # Get the name of the activity
        name = self.container.components[2].text
        # Get the priority of the activity
        priority = self.container.components[4].index
        # Read the activities
        activities = read_activities('activities.txt')
        # Add the new activity
        activities.append(Activity(name, priority))
        # Write the activities back to file
        write_activities('activities.txt', activities)
        # Regress the state
        self.regress_state()
