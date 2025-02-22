import discord
from discord.ext import commands


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.user_command()
    async def greet(self, ctx, member: discord.Member):
        await ctx.respond(f"{ctx.author.mention} says hello world to {member.mention}!")

    # creates a global message command. use guild_ids=[] to create guild-specific commands.
    @discord.message_command(name="Get Message ID")
    async def get_message_id(ctx, message: discord.Message):
        # message commands return the message
        await ctx.respond(f"Message ID: `{message.id}`")

    # creates a global message command. use guild_ids=[] to create guild-specific commands.
    @discord.message_command(name="Get Message ID")
    async def get_message_id(ctx, message: discord.Message):
        # message commands return the message
        await ctx.respond(f"Message ID: `{message.id}`")


def setup(bot):
    bot.add_cog(Test(bot))
