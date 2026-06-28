# Later™

Discord bot that lets you snooze specific messages, reminding you about them later.
Still in development, don't expect totally safe migrations if you host it yourself.

## Features

- Use the Discord apps context menu on ANY message to set a reminder from ANYWHERE
  - Pick between a preset reminder duration or specify a time with natural language (ex. `2 hours`, `10 minutes`)
  - Works regardless of your permissions in the channel, server, or DM
  - Setting a reminder is not seen by other users
- Reminders are delivered to you `@silent`ly by a DM from the bot
  - The notification contains a link back to the message and when you asked to be reminded about it
- `/check-reminders`: Check pending reminders in your DMs with the bot
  - Reschedule or cancel any reminder
- React to any (non-ephemeral) bot-sent message with `❌` and the bot will delete it
  - For cleaning up reminder messages in your DMs with the bot

## Usage

Add the bot to your server with this link: (TODO, contact Robb directly or host it yourself)

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
One unsafe way to do that is to run `chmod 777 .` from inside the data folder.
You could also run the container as root via `user: "0:0"` in the compose file, which is also unsafe, and doesn't let you edit it via a share.
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
    - Note: changes to modals, views, etc. seem to require full bot restart even if made class members of a cog
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
- The bot will automatically create an empty database (`./data/laterbot-tortoise.sqlite3`) if it doesn't find one at startup
- Linter rule help <https://pylint.readthedocs.io/en/latest/user_guide/messages/message_control.html>
- Some things will hot reload and some won't because discord caches them, not totally sure what does/doesn't work yet

### Launching

To run the bot for local testing, use `python .\src\laterbot` from the project root directory, or use the VSCode "Debug LaterBot" Run & Debug action.

### Testing the Docker Container Locally

To locally test the docker container, create a copy of `docker-compose-localtest.example.yml` to fill in the env vars, then run:

```powershell
docker compose -f .\docker-compose-localtest.yml up --build
```

### Migrations

Migrations must be run after adding or changing database models.

[Aerich](https://github.com/tortoise/aerich) is used for migrations and is installed by pip.

To create the database for the first time on a new machine, run this from the project root directory:

```sh
aerich init-db
```

To make a new migration, use `aerich migrate --name migration_name_here` from the project root directory.

Find more info on Aerich with Tortoise here: <https://tortoise.github.io/migration.html>

Apparently [the Aerich dev doesn't want to officially support sqlite](https://github.com/tortoise/aerich/issues/40#issuecomment-690819632) so you may need to write a bunch of migrations manually.
To make an empty migration file to edit manually, use `aerich migrate --name migration_name_here --empty`.

### Releases

Docker buildx is used to prepare container packages.

Build and upload packages (credentials required) via:

```sh
sh build-and-push.sh
```

## Future

- CI/CD pipeline (for now, see [NOTES.md](NOTES.md) for manual publish instructions)
- Intelligent reminder distribution loop (instead of a fixed interval, wait until the next reminder is due, unless one is scheduled sooner)
- Per-user "remind at" preset times
- User timezone awareness for natural language processing time inputs (user settings and/or ask in a second modal field)
- Development time hot reloading for Views, Modals, Buttons
- Auto db cleanup of delivered reminders
- More robust error handling
