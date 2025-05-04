import discord
from db.models.user import User
from discord import IntegrationType, InteractionContextType
from discord.ext import commands


class UserSettings(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.slash_command(
        name="options",
        description="Check what your preferences are set to",
        contexts={InteractionContextType.bot_dm},
        integration_types={IntegrationType.user_install},
    )
    async def check_reminders(self, ctx: discord.ApplicationContext):
        user_id = ctx.author.id

        user, _ = await User.get_or_create_from_discord_user_id(discord_user_id=user_id)

        embed = discord.Embed(
            title=f"User Details",
            description=user,
            color=discord.Color.blue(),
        )

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(UserSettings(bot))
