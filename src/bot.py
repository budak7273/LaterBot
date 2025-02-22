import discord
import ezcord
from cogwatch import Watcher
from dotenv import load_dotenv

from utils.env import get_env

load_dotenv()  # load all the variables from the env file

bot = ezcord.Bot(error_webhook_url=get_env("error_webhook_url"))

print("Loading bot...")


@bot.event
async def on_ready():
    # Use cogwatch to (hot) reload cogs
    # Note: preload does not seem to update discord's app command records so we still need to load_extension each cog first like above
    watcher = Watcher(bot, path="cogs", preload=False, debug=True)
    await watcher.start()


if __name__ == "__main__":
    bot.load_cogs("cogs")

    bot.run(get_env("TOKEN"))

    print("Bot exited.")
