import ezcord
from cogwatch import Watcher
from dotenv import load_dotenv
from ezcord import log
from tortoise import Tortoise

from utils.env import get_env

load_dotenv()


class LaterBot(ezcord.Bot):

    # def run(self, token: str, **kwargs):
    #     """
    #     Override enable db setup
    #     """
    #     super().run(**kwargs)

    async def close(self):
        """
        Override to close db connections
        """
        log.info("Closing database connections...")
        await Tortoise.close_connections()
        log.info("Database connections closed.")
        await super().close()


bot = LaterBot(error_webhook_url=get_env("error_webhook_url"))

print("Loading bot...")


@bot.event
async def on_ready():
    log.info("on_ready (can be called multiple times)")


@bot.listen("on_ready", once=True)
async def first_on_ready():
    """Called only once per bot startup"""
    log.info("first_on_ready (called only once)")

    # Use cogwatch to (hot) reload cogs
    # Note: preload does not seem to update discord's app command records; still requires bot restart
    # which is why ezcord bot.load_cogs is still used
    watcher = Watcher(bot, path="cogs", preload=False, debug=True)
    await watcher.start()

    log.info("Connecting to database...")
    await Tortoise.init(
        db_url="sqlite://laterbot-tortoise.sqlite3",
        modules={"models": ["db.models.reminders"]},
    )
    log.info("Database connection established.")


def startup():
    bot.load_cogs("cogs")

    bot.run(get_env("TOKEN"))

    print("Bot exited.")


if __name__ == "__main__":
    startup()
