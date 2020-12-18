import subprocess
from time import sleep
from datetime import datetime

import click
import questionary

from tally.storage import (
    add_tally,
    get_count,
    get_counts_today
)

INTERVAL_MINUTES = .25

INTERVAL_SECONDS = INTERVAL_MINUTES * 60
ALLIGN_TO_HOUR = True

activities = [
    "Body Squats",
    "Pushups",
    "Pullups",
]

def get_user_activity(activities, status=""):
    # messagebox.showinfo("Title", "message")
    # activities_str = '"' + '", "'.join(activities + ["Nothing"]) + '"'
    activities_str = '"' + '", "'.join(activities) + '"'
    # click.echo(activities_str)

    applescript = f"""
    display dialog "{status}What did you do this time?" ¬
    with title "Tally" ¬
    with icon stop ¬
    giving up after {INTERVAL_SECONDS - 5} ¬
    buttons {{{activities_str}}}
    """

    selection = str(subprocess.check_output(f"osascript -e '{applescript}'", shell=True))

    if "gave up:true" in selection:
        return False

    return selection

@click.group()
@click.option("-d", "--decrement", is_flag=True)
@click.option("-c", "--count", is_flag=True)
def tally(decrement, count):
    """Keep tally for arbitrary strings"""


@click.command()
@click.argument("label")
def add(label):
    click.echo(add_tally(label))

@click.command()
@click.argument("label")
def count(label):
    click.echo(get_count(label))

@click.command()
def run():
    loop = True
    while loop:
        click.echo(datetime.now().minute)
        click.echo(INTERVAL_SECONDS)

        status = ""
        status += "Today, you have done:"
        for activity in activities:
            status += f"\n{activity}: {get_count(activity)}"
        status += "\n\n"

        click.echo(status)
        selection = get_user_activity(activities, status=status)

        if selection:
            click.echo(selection)
            add_tally(selection)
        else:
            click.echo("Cancelled automatically")


        # selection = questionary.select(
        #     "What did you do this time?",
        #     choices=activities
        # ).ask()
        # click.echo("Great job!")


        # selection = click.prompt("What did you do this time?", type=str)
        sleep(INTERVAL_SECONDS)




tally.add_command(add)
tally.add_command(count)
tally.add_command(run)

if __name__ == '__main__':
    tally()
