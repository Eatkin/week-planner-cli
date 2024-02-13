"""Activity class object"""

class Activity:
    def __init__(self, choice, priority):
        self.choice = choice
        self.priority = priority

    def get_activity(self):
        return self.choice

def read_activities(filename):
    activities = []
    with open(filename) as f:
        for line in f:
            choice, priority = ",".join(line.strip().split(',')[:-1]), line.strip().split(',')[-1]
            activities.append(Activity(choice, int(priority)))
    return activities

def write_activities(filename, activities):
    with open(filename, 'w') as f:
        for activity in activities:
            f.write(f"{activity.choice},{activity.priority}\n")
