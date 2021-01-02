import subprocess
from dataclasses import dataclass
from time import sleep
from datetime import datetime

import fire
import questionary

from tally.storage import Storage

storage = Storage("sqlite:///tally.db")

# TODO: change sleep to something like sleep_until
# see https://stackoverflow.com/questions/2031111/in-python-how-can-i-put-a-thread-to-sleep-until-a-specific-time

INTERVAL_MINUTES = 15

INTERVAL_SECONDS = INTERVAL_MINUTES * 60
# INTERVAL_SECONDS = 1

ALLIGN_TO_HOUR = True
SELECT_DIALOG = True

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

def get_user_activity(activities, status="", default=None):
    # messagebox.showinfo("Title", "message")
    # activities_str = '"' + '", "'.join(activities + ["Nothing"]) + '"'
    activities_str = '"' + '", "'.join(activities) + '"'
    # echo(activities_str)

    prompt = "What did you do this time?"

    if default is None:
        default = activities[0]

    if SELECT_DIALOG:

        applescript = f"""
        set choices to {{{activities_str}}}
        set choice to choose from list choices with prompt "{status}{prompt}" default items {{"{default}"}}
        choice
        """
        selection = subprocess.check_output(f"osascript -e '{applescript}'", shell=True).decode().strip()

        echo(selection)

        if selection == "false":
            return False

        return selection

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

def sleep_loop():
    if ALLIGN_TO_HOUR:
        # sleep(5)
        sleep_seconds = INTERVAL_SECONDS - ((datetime.now().minute % INTERVAL_MINUTES) * 60) - datetime.now().second
        echo(f"sleep_seconds: {sleep_seconds}")
        sleep(sleep_seconds)
    else:
        sleep(INTERVAL_SECONDS)

def echo(echo_string):
    print(echo_string)


@dataclass
class Tally(object):
    """Keep tally for arbitrary strings"""
    on_hour: bool = True

    def add(self, label):
        echo(storage.add_tally(label))

    def count(self, label=None, all=False):
        if all:
            echo(storage.get_counts_all())
        else:
            if label is None:
                echo(storage.get_counts_today())
            else:
                echo(storage.get_count(label))

    def run(self):
        loop = True
        last_prompted = False
        while loop:
            current_minute = datetime.now().minute
            current_second = datetime.now().second
            echo(f"{current_minute}:{current_second}")
            echo(f"INTERVAL_SECONDS: {INTERVAL_SECONDS}")

            if self.on_hour:
                if current_minute % INTERVAL_MINUTES != 0 or current_minute == last_prompted:
                    sleep_loop()

            status = ""
            # status += "Today, you have done:"
            default_activity = activities[0]
            for activity in activities:
                activity["count"] = storage.get_count(activity["label"])
                if activity["count"] < default_activity["count"]:
                    default_activity = activity
                status += f'{activity["label"]}: {activity["count"]}/{activity["goal"]}\n'
            # status += "\n\n"

            echo(status)
            echo(f'Do next: {default_activity["label"]}')
            activities_list = (a["label"] for a in activities)
            selection = get_user_activity(activities_list, status=status, default=default_activity["label"])

            if selection:
                echo(selection)
                storage.add_tally(selection)
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
                activity["count"] = storage.get_count(activity["label"])
                if activity["count"] < activity["goal"]:
                    loop = True
            if not loop:
                tell_finished()
                break


            sleep_loop()
            # selection = click.prompt("What did you do this time?", type=str)


def main():
    fire.Fire(Tally)

if __name__ == '__main__':
    main()
