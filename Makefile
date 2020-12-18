
.PHONY: build
build:
	pipx uninstall tally && pipx install . -e

run:
	export FLASK_APP=tally/api.py && pipenv run flask run

try:
	pipenv run python tally/cli.py "Body Squats"