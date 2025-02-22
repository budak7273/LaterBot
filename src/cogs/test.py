import discord
from discord.ext import commands
from ezcord import emb, log

from db.db import db


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
        result = await db.get_users()
        await emb.success(ctx, f"Result: {result}")

    @commands.message_command(name="Get DB Row")
    async def get_message_id(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ):
        # await emb.error(ctx, "Error message")
        # await emb.info(ctx, "Info message", title="Info Title")  # set an embed title
        # await ctx.respond(f"Message ID: `{message.id}`")

        await db.add_coins(12345, 100)
        result = await db.get_one_user(12345)
        log.info(str(result))  # (12345, 100)
        await emb.success(ctx, f"Result: {result}")


def setup(bot):
    bot.add_cog(Test(bot))
