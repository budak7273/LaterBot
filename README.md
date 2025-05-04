# Later™

Discord bot that lets you snooze specific messages, reminding you about them later.

## Usage

Add the bot to your server with this link: TODO

All bot interactions are performed via the discord Apps context menu or via slash commands in DMs with the bot user.

## Hosting

If you want to host the bot yourself, use the docker container: TODO

To run the bot without the container, follow the Development instructions below.

## Stack

- Developed on Windows in VSCode
- Python
  - The repo's `.python-version` file indicates the version to use
    - `pyenv install versionHere`, `pyenv local versionHere`
- [Pycord](https://github.com/Pycord-Development/pycord)
  - [Ezcord](https://github.com/tibue99/ezcord)
    - Logging and error handling
  - [cogwatch](https://github.com/robertwayne/cogwatch/) to reload cogs at runtime
    - Note: changes to application command names/syntax still requires a full bot restart
- Sqlite (probably switch to postgres later)
  - Tortoise ORM

## Development

- Clone the repo
- Install/select the correct python version using pyenv
  - The repo's `.python-version` file indicates the version to use
  - Install using [pyenv-win](https://github.com/pyenv-win/pyenv-win)
    - `pyenv install versionHere`, `pyenv local versionHere`
- Remember to make python venv (`python -m venv venv`)
- Remember to activate python venv (`.\venv\Scripts\Activate.ps1`)
- Install requirements `pip install -r .\requirements.txt`
  - NOTE: Until pycord fixes their stuff, `audioop-lts; python_version>='3.13'` is needed. The requirements file should take care of this for you.
- Set up the `.env` file with a bot token.
- For first time db setup, use `python .\db-init.py` in the `/src/` directory. TODO aerich
- When running, use `python .\src\laterbot` from the project root directory.
- Linter rule help <https://pylint.readthedocs.io/en/latest/user_guide/messages/message_control.html>

### Migrations

Migrations must be run after adding or changing datbase models.

[Aerich](https://github.com/tortoise/aerich) is used for migrations and is installed by pip.

To create the database for the first time on a new machine, run this from the project root directory:

```sh
aerich init-db
```

To make a new migration, use `aerich migrate --name migration_name_here` from the project root directory.

Find more info on Aerich with Tortoise here: <https://tortoise.github.io/migration.html>

Apparently [the Aerich dev doesn't want to officially support sqlite](https://github.com/tortoise/aerich/issues/40#issuecomment-690819632) so you may need to write a bunch of migrations manually.
To make an empty migration file to edit manually, use `aerich migrate --name migration_name_here --empty`.

## Future

- Docker container
- CI/CD pipeline
- Intelligent reminder distribution loop (instead of a fixed interval, wait until the next reminder is due, unless one is scheduled sooner)
- Per-user "remind at" preset times
- Auto db cleanup of delivered reminders
- More robust error handling
