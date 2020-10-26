# Intended to be run within Docker backend container during development
SRC_FILES := $(shell find ./src -name *.py)
APPS := webapp users
TEST_OPTIONS := --keepdb
POETRY_RUN := poetry run
POETRY_MANAGE := $(POETRY_RUN) /var/www/src/manage.py

install :
	python3.7 -m venv .venv
	poetry install
	$(POETRY_MANAGE) migrate
	$(POETRY_MANAGE) setup_skeletons
	$(POETRY_MANAGE) collectstatic --no-input

test :
	poetry run python -Wall /var/www/src/manage.py test $(TEST_OPTIONS) $(APPS)
