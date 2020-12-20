import subprocess
from time import sleep
from datetime import datetime

import click
import questionary

from tally.storage import Storage

storage = Storage()

# TODO: change sleep to something like sleep_until
# see https://stackoverflow.com/questions/2031111/in-python-how-can-i-put-a-thread-to-sleep-until-a-specific-time

# TODO: add goal per activity
# TODO: cycle through default button based on lowest tally relative to goal

INTERVAL_MINUTES = 15

INTERVAL_SECONDS = INTERVAL_MINUTES * 60
INTERVAL_SECONDS = 2

ALLIGN_TO_HOUR = False
SELECT_DIALOG = True

activities = [
    "Body Squats",
    "Pushups",
    "Pullups",
]

def get_user_activity(activities, status="", default=None):
    # messagebox.showinfo("Title", "message")
    # activities_str = '"' + '", "'.join(activities + ["Nothing"]) + '"'
    activities_str = '"' + '", "'.join(activities) + '"'
    # click.echo(activities_str)

    if default is None:
        default = activities[0]

    if SELECT_DIALOG:

        applescript = f"""
        set choices to {{{activities_str}}}
        set choice to choose from list choices with prompt "What did you do this time?" default items {{"{default}"}}
        choice
        """
        selection = subprocess.check_output(f"osascript -e '{applescript}'", shell=True).decode().strip()

        click.echo(selection)

        if selection == "false":
            return False

        return selection

    else:
        applescript = f"""
        display dialog "{status}What did you do this time?" ¬
        with title "Tally" ¬
        with icon stop ¬
        giving up after {INTERVAL_SECONDS - 60} ¬
        buttons {{{activities_str}}}
        """
        selection = str(subprocess.check_output(f"osascript -e '{applescript}'", shell=True))
        if "gave up:true" in selection:
            return False

        selection = selection.split(":")[1]
        selection = selection.split(",")[0]

        return selection



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
        status += "Today, you have done:"
        for activity in activities:

            status += f"\n{activity}: {storage.get_count(activity)}"
        status += "\n\n"

        click.echo(status)
        selection = get_user_activity(activities, status=status, default=activities[1])

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

        sleep_loop()
        # selection = click.prompt("What did you do this time?", type=str)

tally.add_command(add)
tally.add_command(count)
tally.add_command(run)

if __name__ == '__main__':
    tally()
