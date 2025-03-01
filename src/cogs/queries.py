from datetime import datetime, timezone

import discord
from discord.enums import IntegrationType, InteractionContextType
from discord.ext import commands
from ezcord import log

from db.models.reminder import Reminder


class Queries(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(
        name="check_reminders",
        description="Check your upcoming reminders",
        contexts={InteractionContextType.bot_dm},
        integration_types={IntegrationType.user_install},
    )
    async def check_reminders(self, ctx: discord.ApplicationContext):
        user_id = ctx.author.id

        reminders = await Reminder.filter(
            discord_user_id=user_id,
            errored=False,
            delivered=False,
        ).order_by("remind_at")

        if not reminders:
            await ctx.respond("You have no upcoming reminders.", ephemeral=True)
            return

        reminder_list = "\n".join(
            [
                f"- <t:{int(reminder.remind_at.timestamp())}:R> - {reminder.target_message_jump_url} - id:`{reminder.id}`"
                for reminder in reminders
            ]
        )

        current_time = int(datetime.now(tz=timezone.utc).timestamp())
        embed = discord.Embed(
            title=f"Your Upcoming Reminders (As of <t:{current_time}:F>)",
            description=reminder_list,
            color=discord.Color.blue(),
        )

        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Queries(bot))
