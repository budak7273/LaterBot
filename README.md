# Later™

Discord bot that lets you snooze specific messages, reminding you about them later.

## Usage

Add the bot to your server with this link: TODO

## Stack

- Developed on windows
- [pyenv-win](https://github.com/pyenv-win/pyenv-win)
- Python `pyenv install versionHere`, `pyenv local versionHere`
  - The repo's `.python-version` file indicates the version to use
- Activate python venv (`.\venv\Scripts\Activate.ps1`)
- Install requirements `pip install -r .\requirements.txt`
  - NOTE: Until pycord fixes their stuff, may need to install `audioop-lts; python_version>='3.13'`

## Development

Set up the `.env` file with a bot token.

Make sure to activate the venv if your editor doesn't do so automatically (see above).

When running, use `python .\bot.py` in the `/src/` directory.

Linter rule help <https://pylint.readthedocs.io/en/latest/user_guide/messages/message_control.html>
