import os

import discord
from cogwatch import Watcher
from dotenv import load_dotenv

load_dotenv()  # load all the variables from the env file
bot = discord.Bot()

print("Loading bot...")

cogs_list = ["test", "snooze"]

for cog in cogs_list:
    bot.load_extension(f"cogs.{cog}")


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

    # Use cogwatch to (hot) reload cogs
    # Note: preload does not seem to update discord's app command records so we still need to load_extension each cog first like above
    watcher = Watcher(bot, path="cogs", preload=True, debug=True)
    await watcher.start()


@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")


@bot.slash_command(name="hello3", description="Say hello to the bot 3")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey! 3")


# @bot.user_command(name="Account Creation Date", )  # create a user command for the supplied guilds
# async def account_creation_date(ctx, member: discord.Member):  # user commands return the member
#     await ctx.respond(f"{member.name}'s account was created on {member.created_at}")

bot.run(os.getenv("TOKEN"))  # run the bot with the token

print("Bot exited.")
