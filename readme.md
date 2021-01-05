### Tally

I am building a habit of doing one set of a few basic exercises every 15 minutes of the day. There are a lot of apps that kind of do what I wanted, but I couldn't find one that did it exactly.

If you're interested in using this, I can help you get it running on your computer.

### Requirements
- MacOS (AppleScript dialog boxes)
- Python (I've only used version 3.9)
- [Pipenv](https://pipenv.pypa.io/en/latest/)
- [pipx](https://pipxproject.github.io/pipx/)

### Getting started

1. Clone this repo
2. Install dependencies (maybe don't need this step?)
3. Install for local use with pipx (I'll probably distribute it here someday)

To do this on the command line:
```
git clone git@github.com:sunfarm/tally.git
cd tally
make install
make build-dev
```

### How I Got Here

I usually like to write down the first few commands I run to get a project started for future reference. Some of these no longer apply to the project.

```
mkcd tally
touch setup_process.md
edit .

mkdir tally
touch tally/__init__.py
touch tally/api.py

touch tally/storage.py

pipenv install flask


touch Makefile

pipenv install click
touch tally/cli.py
pipenv install sqlalchemy
```