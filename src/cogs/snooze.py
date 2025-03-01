from datetime import datetime, timedelta, timezone

import discord
from discord.enums import IntegrationType, InteractionContextType
from discord.ext import commands
from ezcord import log

from db.models.reminder import Reminder


def create_reminder_embed(
    message: discord.Message, remind_at: datetime, footer_text: str
) -> discord.Embed:
    epoch_timestamp = int(remind_at.timestamp())
    embed = discord.Embed(
        title=":white_check_mark: Reminding you Later™",
        description=f"Got it - you'll be reminded about {message.jump_url} <t:{epoch_timestamp}:R> (<t:{epoch_timestamp}:F>)!",
        color=discord.Color.green(),
    )
    embed.set_footer(text=footer_text)
    return embed


class CustomSnoozeModal(discord.ui.Modal):
    def __init__(
        self, message: discord.Message, original_interaction: discord.Interaction
    ):
        super().__init__(title="Custom Snooze Duration")

        self.message = message
        self.original_interaction = original_interaction

        self.add_item(
            discord.ui.InputText(
                label="Custom Duration (seconds)",
                placeholder="Enter custom duration in seconds",
                required=True,
                custom_id="custom_duration",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        custom_duration_input: discord.ui.InputText = self.children[0]
        duration = int(custom_duration_input.value)

        current_utc_time = datetime.now(timezone.utc)
        remind_at = current_utc_time + timedelta(seconds=duration)

        embed = create_reminder_embed(self.message, remind_at, "Snooze...")

        reminder = await Reminder.create(
            discord_user_id=interaction.user.id,
            remind_at=remind_at,
            target_message_id=self.message.id,
            target_message_channel_id=self.message.channel.id,
            target_message_jump_url=self.message.jump_url,
        )
        log.info(f"New reminder created with id {reminder.id}")

        await self.original_interaction.edit_original_message(
            content="", embed=embed, view=None
        )


class SnoozeSelect(discord.ui.Select):
    def __init__(
        self, message: discord.Message, original_interaction: discord.Interaction
    ):
        self.message = message
        self.original_interaction = original_interaction
        options = [
            discord.SelectOption(label="1 hour", value="3600"),
            discord.SelectOption(label="6 hours", value="21600"),
            discord.SelectOption(label="12 hours", value="43200"),
            discord.SelectOption(label="Custom", value="custom"),
        ]
        super().__init__(
            placeholder="Choose a duration...",
            options=options,
            custom_id="duration_select",
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "custom":
            modal = CustomSnoozeModal(self.message, self.original_interaction)
            await interaction.response.send_modal(modal)
        else:
            duration = int(self.values[0])
            current_utc_time = datetime.now(timezone.utc)
            remind_at = current_utc_time + timedelta(seconds=duration)

            embed = create_reminder_embed(self.message, remind_at, "Snooze...")

            reminder = await Reminder.create(
                discord_user_id=interaction.user.id,
                remind_at=remind_at,
                target_message_id=self.message.id,
                target_message_channel_id=self.message.channel.id,
                target_message_jump_url=self.message.jump_url,
            )
            log.info(f"New reminder created with id {reminder.id}")

            await self.original_interaction.edit_original_message(
                content="", embed=embed, view=None
            )


class SnoozeView(discord.ui.View):
    def __init__(
        self, message: discord.Message, original_interaction: discord.Interaction
    ):
        super().__init__()
        self.add_item(SnoozeSelect(message, original_interaction))


class Snooze(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    async def real_quick_snooze_message(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ):
        current_utc_time = datetime.now(timezone.utc)
        remind_at = current_utc_time + timedelta(seconds=5)

        embed = create_reminder_embed(message, remind_at, "Quick Snooze")

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

    @commands.message_command(
        name="Snooze...",
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
    async def snooze_message(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ):
        view = SnoozeView(message, ctx.interaction)
        await ctx.respond("Choose a duration for the reminder:", view=view)


def setup(bot: discord.Bot):
    bot.add_cog(Snooze(bot))
