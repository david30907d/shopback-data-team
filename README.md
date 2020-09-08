# Shopback Data team assignment ![Docker Image CI](https://github.com/david30907d/shopback-data-team/workflows/Docker%20Image%20CI/badge.svg)

Just Assignment.

## Install

1. Python dependencies:
    1. `virtualenv venv; . venv/bin/activate`
    2. `pip install poetry`
    3. `poetry install`
2. Npm dependencies, for linter, formatter and commit linter (optional):
    1. `brew install npm`
    2. `npm ci`

## How to Develop

1. Commit using commitizen UI: `npm run commit`

    ![img](https://github.com/commitizen/cz-cli/raw/master/meta/screenshots/add-commit.png)

## Run

1. Invoke: `python3 main.py`
2. test: `npm run test`
3. Run all linter before commitment would save some effort: `npm run check`

## CI/CD

Please check [.github/workflows](.github/workflows/)