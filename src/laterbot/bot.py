import os
import traceback

import ezcord
from cogwatch import Watcher
from db.config import TORTOISE_ORM_FOR_BOT
from dotenv import load_dotenv
from ezcord import log
from tortoise import Tortoise
from utils.env import get_env

load_dotenv()

# Set the working directory to folder containing this file (makes it easier to run from anywhere)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print(f"Using working directory: {os.getcwd()}")


class LaterBot(ezcord.Bot):

    async def close(self):
        """
        Overridden to close db connections on exit
        """
        log.info("Closing database connections...")
        await Tortoise.close_connections()
        log.info("Database connections closed.")
        await super().close()


bot = LaterBot(error_webhook_url=get_env("error_webhook_url"))


@bot.event
async def on_ready():
    log.info("on_ready (can be called multiple times)")


@bot.listen("on_ready", once=True)
async def first_on_ready():
    """Called only once per bot startup"""
    log.info("first_on_ready (called only once)")

    # Use cogwatch to hot reload cogs
    # Note: preload does not seem to update discord's app command records; still requires bot restart
    # which is why ezcord bot.load_cogs() is still used in startup()
    watcher = Watcher(bot, path="cogs", preload=False, debug=True)
    await watcher.start()

    log.info("Connecting to database...")
    try:
        await Tortoise.init(config=TORTOISE_ORM_FOR_BOT)
    except Exception as e:
        log.error(f"Error connecting to database: {traceback.format_exc()}")
        exit(1)
    log.info("Database connection established.")


def startup():
    print("Loading bot...")

    bot.load_cogs("cogs")

    bot.run(get_env("TOKEN"))

    print("Bot exited.")
