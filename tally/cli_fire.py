import subprocess
from dataclasses import dataclass, field
from time import sleep
from datetime import datetime

import fire
import questionary

from tally.storage import Storage

# TODO: change sleep to something like sleep_until
# see https://stackoverflow.com/questions/2031111/in-python-how-can-i-put-a-thread-to-sleep-until-a-specific-time

activities = [
    {
        "label": "Body Squats",
        "goal": 10,
        "value": 10,
        "unit": "repetitions",
    },
    {
        "label": "Plank",
        "goal": 10,
        "value": 30,
        "unit": "seconds",
    },
    {
        "label": "Pushups",
        "goal": 10,
        "value": 10,
        "unit": "repetitions",
    },
    {
        "label": "Crunches",
        "goal": 10,
        "value": 10,
        "unit": "repetitions",
    },
    {
        "label": "Pullups",
        "goal": 10,
        "value": 5,
        "unit": "repetitions",
    },
    {
        "label": "Superman",
        "goal": 10,
        "value": 15,
        "unit": "seconds",
    },
]

def run_applescript(applescript):
    return str(subprocess.check_output(f"osascript -e '{applescript}'", shell=True))



def notify(title="Tally", subtitle="", message=""):
    applescript = f"""
    display notification "{message}" with title "{title}" subtitle "{subtitle}"
    """
    run_applescript(applescript)

def tell_finished():
    title = "Tally"
    subtitle = "Great jobs!"
    message = "You met your goals for the day!"
    echo(message)
    notify(title, subtitle, message)

def echo(echo_string):
    print(echo_string)


@dataclass
class Tally(object):
    """Keep tally for arbitrary strings"""
    on_hour: bool = True
    interval: int = 15
    use_select_dialog: bool = True
    database_name: str = "tally.db"
    storage: Storage = field(init=False)

    def __post_init__(self):
        if self.database_name:
            self.storage = Storage(f"sqlite:///{self.database_name}")
        else:
            self.storage = Storage()


    def add(self, label):
        echo(self.storage.add_tally(label))

    def count(self, label=None, all=False):
        if all:
            echo(self.storage.get_counts_all())
        else:
            if label is None:
                echo(self.storage.get_counts_today())
            else:
                echo(self.storage.get_count(label))


    def interval_seconds(self):
        return self.interval * 60


    def sleep_loop(self):
        if self.on_hour:
            sleep_seconds = self.interval_seconds() - ((datetime.now().minute % self.interval) * 60) - datetime.now().second
            echo(f"Sleeping for {sleep_seconds} seconds")
            sleep(sleep_seconds)
        else:
            sleep(self.interval_seconds())


    def run(self):
        loop = True
        last_prompted = False
        while loop:
            current_minute = datetime.now().minute
            current_second = datetime.now().second
            # echo(f"{current_minute}:{current_second}")
            # echo(f"INTERVAL_SECONDS: {self.interval_seconds()}")

            if self.on_hour:
                if current_minute % self.interval != 0 or current_minute == last_prompted:
                    self.sleep_loop()

            status = ""
            # status += "Today, you have done:"
            default_activity = activities[0]
            for activity in activities:
                activity["count"] = self.storage.get_count(activity["label"])
                if activity["count"] < default_activity["count"]:
                    default_activity = activity
                status += f'{activity["label"]}: {activity["count"]}/{activity["goal"]}\n'
            # status += "\n\n"

            echo(status)
            echo(f'Do next: {default_activity["label"]}')
            activities_list = (a["label"] for a in activities)
            selections = self.get_user_activity(activities_list, status=status, default=default_activity["label"])

            if selections:
                echo(selections)
                for selection in selections:
                    self.storage.add_tally(selection)
                last_prompted = current_minute
            else:
                echo("Cancelled automatically")


            # selection = questionary.select(
            #     "What did you do this time?",
            #     choices=activities
            # ).ask()
            # echo("Great job!")

            loop = False
            for activity in activities:
                activity["count"] = self.storage.get_count(activity["label"])
                if activity["count"] < activity["goal"]:
                    loop = True
            if not loop:
                tell_finished()
                break


            self.sleep_loop()
            # selection = click.prompt("What did you do this time?", type=str)


    def get_user_activity(self, activities, status="", default=None):
        # messagebox.showinfo("Title", "message")
        # activities_str = '"' + '", "'.join(activities + ["Nothing"]) + '"'
        activities_str = '"' + '", "'.join(activities) + '"'
        # echo(activities_str)

        prompt = "What did you do this time?"

        if default is None:
            default = activities[0]

        if self.use_select_dialog:
            applescript = f"""
            set choices to {{{activities_str}}}
            set choice to choose from list choices with prompt "{status}{prompt}" default items {{"{default}"}} with multiple selections allowed
            choice
            """
            echo(f"osascript -e '{applescript}'")
            selections = subprocess.check_output(f"osascript -e '{applescript}'", shell=True).decode().strip()

            echo(selections)

            if selections == "false":
                return False

            return selections.split(", ")

        else:
            applescript = f"""
            display dialog "{status}{prompt}" ¬
            with title "Tally" ¬
            with icon stop ¬
            giving up after {INTERVAL_SECONDS - 60} ¬
            buttons {{{activities_str}}}
            """
            # selection = str(subprocess.check_output(f"osascript -e '{applescript}'", shell=True))
            selection = run_applescript(applescript)
            if "gave up:true" in selection:
                return False

            selection = selection.split(":")[1]
            selection = selection.split(",")[0]

            return selection

def main():
    fire.Fire(Tally)

if __name__ == '__main__':
    main()
