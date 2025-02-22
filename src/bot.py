import os
import discord
from dotenv import load_dotenv

load_dotenv()  # load all the variables from the env file
bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")


# @bot.user_command(name="Account Creation Date", )  # create a user command for the supplied guilds
# async def account_creation_date(ctx, member: discord.Member):  # user commands return the member
#     await ctx.respond(f"{member.name}'s account was created on {member.created_at}")

print("Loading bot...")

cogs_list = [
    "test",
]

for cog in cogs_list:
    bot.load_extension(f"cogs.{cog}")

bot.run(os.getenv("TOKEN"))  # run the bot with the token

print("Bot exited.")
