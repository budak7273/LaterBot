from datetime import datetime, timedelta, timezone

import discord
from discord.enums import IntegrationType, InteractionContextType
from discord.ext import commands
from ezcord import log

from db.models.reminder import Reminder


class Snooze(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    async def real_quick_snooze_message(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ):
        current_utc_time = datetime.now(timezone.utc)
        remind_at = current_utc_time + timedelta(seconds=5)

        epoch_timestamp = int(remind_at.timestamp())
        embed = discord.Embed(
            title=":white_check_mark: Reminding you Later™",
            description=f"Got it - you'll be reminded about {message.jump_url} <t:{epoch_timestamp}:R> (<t:{epoch_timestamp}:F>)!",
            color=discord.Color.green(),
        )
        embed.set_footer(text="Quick Snooze")

        reminder = await Reminder.create(
            discord_user_id=ctx.author.id,
            remind_at=remind_at,
            target_message_id=message.id,
            target_message_channel_id=message.channel.id,
            target_message_jump_url=message.jump_url,
        )
        log.info(f"New reminder created with id {reminder.id}")

        await ctx.respond(embed=embed)

    @commands.message_command(
        name="Quick Snooze",
        contexts={
            InteractionContextType.bot_dm,
            InteractionContextType.private_channel,
            InteractionContextType.guild,
        },
        integration_types={
            # IntegrationType.guild_install,
            IntegrationType.user_install
        },
    )
    async def quick_snooze_message(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ):
        await self.real_quick_snooze_message(ctx, message)


def setup(bot: discord.Bot):
    bot.add_cog(Snooze(bot))
