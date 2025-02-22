import discord
from discord.ext import commands
from ezcord import emb


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.user_command()
    async def greet(self, ctx: discord.ApplicationContext, member: discord.Member):
        await ctx.respond(f"{ctx.author.mention} says hello world to {member.mention}!")

    @commands.message_command(name="Get Message ID")
    async def get_message_id(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ):
        await emb.error(ctx, "Error message")
        await emb.info(ctx, "Info message", title="Info Title")  # set an embed title
        await ctx.respond(f"Message ID: `{message.id}`")


def setup(bot):
    bot.add_cog(Test(bot))
