import discord
from discord import IntegrationType, InteractionContextType
from discord.ext import commands
from ezcord import emb, log

from db.models.reminder import Reminder

# class MyView(discord.ui.View):
#     @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="😎")
#     async def button_callback(self, button, interaction):
#         await interaction.response.send_message("You clicked the button!")


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.user_command(
    #     name="Get DB Reminders",
    #     contexts={
    #         InteractionContextType.bot_dm,
    #         InteractionContextType.private_channel,
    #         InteractionContextType.guild,
    #     },
    #     integration_types={
    #         # IntegrationType.guild_install,
    #         IntegrationType.user_install
    #     },
    # )
    # async def get_user_reminders(
    #     self, ctx: discord.ApplicationContext, member: discord.Member
    # ):
    #     log.info(f"Getting reminders for {member.id}")
    #     reminders = await Reminder.filter(discord_user_id=member.id)
    #     await emb.success(ctx, f"Result: {reminders}")

    # @commands.slash_command()
    # async def button_test(self, ctx: discord.ApplicationContext):
    #     # await ctx.respond("Hey!")
    #     await ctx.respond(
    #         "This is a button!", view=MyView()
    #     )  # Send a message with our View class that contains the button


def setup(bot):
    bot.add_cog(Test(bot))
