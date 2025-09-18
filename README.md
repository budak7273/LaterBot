# Later™

Discord bot that lets you snooze specific messages, reminding you about them later.
Still in development, don't expect totally safe migrations if you host it yourself.

## Usage

Add the bot to your server with this link: TODO

All bot interactions are performed via the discord Apps context menu or via slash commands in DMs with the bot user.

## Hosting

The easiest way to host the bot is using the provided Docker container and compose file.
If you want to run the bot without the container, follow the [Development instructions](#development).

The bot uses a sqlite database to store persistent info.
It mounts a volume to persist this and exposes the volume to the host for maintenance if necessary.

To specify environment variables, either make a copy of `docker-compose-prod.example.yml` and edit it
or specify them through your hosting system's preferred approach.

The included `docker-compose.yml` mounts the sqlite DB from `./data/laterbot-tortoise.sqlite3` into the container at `/data/laterbot-tortoise.sqlite3`

```powershell
docker compose -f .\docker-compose-localtest.yml up --detach
```

### Unraid

Deploying this on an Unraid server is relatively straightforward.
Install the [Docker Compose Manager](https://forums.unraid.net/topic/114415-plugin-docker-compose-manager/) plugin
and use `docker-compose-prod.example.yml` as the stack.
You will have to edit the bind source to be a directory somewhere in your Unraid,
such as `/mnt/user/appdata/laterbot/` to be near where other containers put their files.
You will have to use the Unraid terminal to change permissions in that folder to allow writing.
One unsafe way to do that is to run `chmod 777` from inside the data folder.
You could also run the container as root via `user: "0:0"` in the compose file, which is also unsafe.
PR if you find a safe way or have more info.

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
- Sqlite (maybe switch to postgres later)
  - Tortoise ORM

## Development

- Create a new [Discord application](https://discord.com/developers/applications) to get a token.
- Clone the repo
- Install/select the correct python version using pyenv
  - The repo's `.python-version` file indicates the version to use
  - Install using [pyenv-win](https://github.com/pyenv-win/pyenv-win)
    - `pyenv install versionHere`, `pyenv local versionHere`
- Remember to make python venv (`python -m venv venv`)
- Remember to activate python venv (`.\venv\Scripts\Activate.ps1`)
- Install requirements `pip install -r .\requirements.txt`
  - NOTE: Until pycord fixes their stuff, `audioop-lts; python_version>='3.13'` is needed. The requirements file should take care of this for you.
- Set up the `.env` file based on `.env.example`.
- For first time db setup, use `python .\src\db-init.py` from the project root directory. TODO bot can do this on its own now. TODO aerich?
- When running, use `python .\src\laterbot` from the project root directory.
- Linter rule help <https://pylint.readthedocs.io/en/latest/user_guide/messages/message_control.html>

To locally test the docker container, create a copy of `docker-compose-localtest.example.yml` to fill in the env vars, then run:

```powershell
docker compose -f .\docker-compose-localtest.yml up --build
```

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

- CI/CD pipeline
- Intelligent reminder distribution loop (instead of a fixed interval, wait until the next reminder is due, unless one is scheduled sooner)
- Per-user "remind at" preset times
- Auto db cleanup of delivered reminders
- More robust error handling
