import subprocess
from time import sleep
from datetime import datetime

import click
import questionary

from tally.storage import Storage

storage = Storage("sqlite:///tally.db")

# TODO: change sleep to something like sleep_until
# see https://stackoverflow.com/questions/2031111/in-python-how-can-i-put-a-thread-to-sleep-until-a-specific-time

# TODO: add goal per activity
# TODO: cycle through default button based on lowest tally relative to goal

INTERVAL_MINUTES = 15

INTERVAL_SECONDS = INTERVAL_MINUTES * 60
# INTERVAL_SECONDS = 1

ALLIGN_TO_HOUR = True
SELECT_DIALOG = True

activities = [
    {
        "label": "Body Squats",
        "goal": 10,
    },
    {
        "label": "Pushups",
        "goal": 10,
    },
    {
        "label": "Pullups",
        "goal": 10,
    },
]

def run_applescript(applescript):
    return str(subprocess.check_output(f"osascript -e '{applescript}'", shell=True))

def get_user_activity(activities, status="", default=None):
    # messagebox.showinfo("Title", "message")
    # activities_str = '"' + '", "'.join(activities + ["Nothing"]) + '"'
    activities_str = '"' + '", "'.join(activities) + '"'
    # click.echo(activities_str)

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

        click.echo(selection)

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

def tell_finished():
    message = "You met your goals for the day!"
    click.echo(message)
    applescript = f"""
    set message to "{message}"
    display dialog message buttons {"Great!"}"
    """
    run_applescript(applescript)

def sleep_loop():
    if ALLIGN_TO_HOUR:
        # sleep(5)
        sleep_seconds = INTERVAL_SECONDS - ((datetime.now().minute % INTERVAL_MINUTES) * 60) - datetime.now().second
        click.echo(f"sleep_seconds: {sleep_seconds}")
        sleep(sleep_seconds)
    else:
        sleep(INTERVAL_SECONDS)

@click.group()
@click.option("-d", "--decrement", is_flag=True)
@click.option("-c", "--count", is_flag=True)
def tally(decrement, count):
    """Keep tally for arbitrary strings"""


@click.command()
@click.argument("label")
def add(label):
    click.echo(storage.add_tally(label))

@click.command()
@click.argument("label", required=False)
@click.option("-a", "--all", is_flag=True)
def count(label=None, all=False):
    if all:
        click.echo(storage.get_counts_all())
    else:
        if label is None:
            click.echo(storage.get_counts_today())
        else:
            click.echo(storage.get_count(label))

@click.command()
def run():
    loop = True
    last_prompted = False
    while loop:
        current_minute = datetime.now().minute
        current_second = datetime.now().second
        click.echo(f"{current_minute}:{current_second}")
        click.echo(f"INTERVAL_SECONDS: {INTERVAL_SECONDS}")

        if ALLIGN_TO_HOUR:
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

        click.echo(status)
        click.echo(f'Do next: {default_activity["label"]}')
        activities_list = (a["label"] for a in activities)
        selection = get_user_activity(activities_list, status=status, default=default_activity["label"])

        if selection:
            click.echo(selection)
            storage.add_tally(selection)
            last_prompted = current_minute
        else:
            click.echo("Cancelled automatically")


        # selection = questionary.select(
        #     "What did you do this time?",
        #     choices=activities
        # ).ask()
        # click.echo("Great job!")

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

tally.add_command(add)
tally.add_command(count)
tally.add_command(run)

if __name__ == '__main__':
    tally()
