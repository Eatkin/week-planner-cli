import calendar
import curses
import random
import os
import logging
from datetime import datetime

from activity import read_activities
from components import Container, Label, Combobox, Button

state_history = []

class State:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.container = None
        self.next_state = None
        state_history.append(self)

    def update(self):
        if self.next_state:
            # Store this state so we can clear it
            state = self.next_state
            self.next_state = None
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
        self.container.add_component(Button, ["Back", lambda: self.regress_state()])
        self.container.add_component(Button, ["Quit", lambda: exit(1)])
