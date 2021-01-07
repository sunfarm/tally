list:
	@echo Available targets:
	@echo
	@grep "^[-a-z]*:" Makefile | cut -f1 -d ':'
	@echo

.PHONY: build-dev
build-dev:
	pipx uninstall tally && pipx install . -e

install:
	pipenv install

run:
	export FLASK_APP=tally/api.py && pipenv run flask run

try:
	pipenv run python tally/cli.py "Body Squats"

format:
	pipenv run black .