import discord
from discord.ext import commands
from ezcord import emb, log

from db.db import db
from db.models.reminders import Reminder


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.user_command()
    async def greet(self, ctx: discord.ApplicationContext, member: discord.Member):
        await ctx.respond(f"{ctx.author.mention} says hello world to {member.mention}!")

    @commands.user_command(name="Get DB Reminders")
    async def get_user_reminders(
        self, ctx: discord.ApplicationContext, member: discord.Member
    ):
        log.info(f"Getting reminders for {member.id}")
        reminders = await Reminder.filter(discord_user_id=member.id)
        await emb.success(ctx, f"Result: {reminders}")

    @commands.message_command(name="Get DB Row")
    async def get_message_id(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ):

        await db.add_coins(12345, 100)
        result = await db.get_one_user(12345)
        log.info(str(result))  # (12345, 100)
        await emb.success(ctx, f"Result: {result}")


def setup(bot):
    bot.add_cog(Test(bot))
