# Later™

Discord bot that lets you snooze specific messages, reminding you about them later.

## Usage

Add the bot to your server with this link: TODO

## Stack

- Developed on Windows in VSCode (see)
- Python
  - The repo's `.python-version` file indicates the version to use
  - Install using [pyenv-win](https://github.com/pyenv-win/pyenv-win)
    - `pyenv install versionHere`, `pyenv local versionHere`
- [Pycord](https://github.com/Pycord-Development/pycord)
  - [Ezcord](https://github.com/tibue99/ezcord)
  - [cogwatch](https://github.com/robertwayne/cogwatch/) to reload cogs at runtime
    - Note: changes to application command names/syntax still requires a full bot restart
- Sqlite (probably switch to postgres later)

## Development

- Remember to make python venv (`python -m venv venv`)
- Remember to activate python venv (`.\venv\Scripts\Activate.ps1`)
- Install requirements `pip install -r .\requirements.txt`
  - NOTE: Until pycord fixes their stuff, `audioop-lts; python_version>='3.13'` is needed. This is in the requirements file.
- Set up the `.env` file with a bot token.
- For first time db setup, use `python .\db-init.py` in the `/src/` directory.
- When running, use `python .\bot.py` in the `/src/` directory.
- Linter rule help <https://pylint.readthedocs.io/en/latest/user_guide/messages/message_control.html>

## Future

- Docker container
- CI/CD pipeline
- DB migrations with [aerich](https://github.com/tortoise/aerich)
- Intelligent reminder distribution loop (instead of a fixed interval, wait until the next reminder is due, unless one is scheduled sooner)
- Per-user "remind at" preset times
- Auto db cleanup of delivered reminders
- More robust error handling
