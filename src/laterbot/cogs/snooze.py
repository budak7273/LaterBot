from datetime import datetime, timedelta, timezone
from typing import Tuple

import dateparser
import discord
from discord.enums import IntegrationType, InteractionContextType
from discord.ext import commands
from discord.ui import View
from ezcord import log

from db.models.reminder import Reminder
from cogs.reminder_ui import ReminderActionView


def create_reminder_embed(
    message: discord.Message,
    remind_at: datetime,
    footer_text: str,
    reminder: Reminder,
) -> Tuple[discord.Embed, View]:
    epoch_timestamp = int(remind_at.timestamp())
    embed = discord.Embed(
        title=":white_check_mark: Reminding you Later™",
        description=f"Got it - you'll be reminded about {message.jump_url} <t:{epoch_timestamp}:R> (<t:{epoch_timestamp}:F>)!",
        color=discord.Color.green(),
    )
    embed.set_footer(text=footer_text)

    view = ReminderActionView(reminder)

    return embed, view


class CustomSnoozeModal(discord.ui.Modal):
    def __init__(self, message: discord.Message, original_interaction: discord.Interaction):
        super().__init__(title="Custom Snooze Duration")

        self.message = message
        self.original_interaction = original_interaction

        self.add_item(
            discord.ui.InputText(
                label="Custom Duration",
                placeholder="e.g., '2 hours', 'tomorrow at 3pm', '30 minutes', 'in 1 day' (TODO sender user timezone handling)",
                required=True,
                custom_id="custom_duration",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        assert interaction.user is not None, "Expected interaction user to be non-None"

        custom_duration_input: discord.ui.InputText = self.children[0]
        assert custom_duration_input.value is not None, "Expected custom duration input to be non-None"

        current_utc_time = datetime.now(timezone.utc)
        user_input = custom_duration_input.value.strip()

        try:
            # Try to parse as natural language using dateparser
            parsed_datetime = dateparser.parse(
                user_input,
                settings={
                    "RETURN_AS_TIMEZONE_AWARE": True,
                    "PREFER_DATES_FROM": "future",
                    "RELATIVE_BASE": current_utc_time,
                },
            )

            print(f"Parsed datetime: {parsed_datetime} ({repr(parsed_datetime)}) from user input: '{user_input}'")

            if parsed_datetime is None:
                await interaction.response.send_message(
                    f"Could not parse '`{user_input}`'. Please try formats like '2 hours', 'tomorrow at 3pm', or '30 minutes'.",
                    ephemeral=True,
                )
                return

            # Does this case ever happen?
            if parsed_datetime.tzinfo is None:
                await interaction.response.send_message(
                    f"Warning: could not detect timezone in '`{user_input}`' Assigning UTC.",
                    ephemeral=True,
                )
                parsed_datetime = parsed_datetime.replace(tzinfo=timezone.utc)

            if parsed_datetime <= current_utc_time:
                timestamp = int(parsed_datetime.timestamp())
                await interaction.response.send_message(
                    f"The time must be in the future. <t:{timestamp}:S> is in the past (request placed at <t:{int(current_utc_time.timestamp())}:S>). Please specify a future time.",
                    ephemeral=True,
                )
                return

            remind_at = parsed_datetime

        except Exception as e:
            log.error(f"Error parsing duration: {e}")
            await interaction.response.send_message(f"Error parsing duration: {str(e)}", ephemeral=True)
            return

        reminder = await Reminder.create(
            discord_user_id=interaction.user.id,
            remind_at=remind_at,
            target_message_id=self.message.id,
            target_message_channel_id=self.message.channel.id,
            target_message_jump_url=self.message.jump_url,
        )
        log.info(f"New reminder created with id {reminder.id}")

        embed, view = create_reminder_embed(self.message, remind_at, "Snooze...", reminder)

        await self.original_interaction.edit_original_response(content="", embed=embed, view=view)
        await interaction.response.defer(invisible=True)

    # TODO is this the correct type arg?
    class SnoozeSelect(discord.ui.Select[View]):
        def __init__(self, message: discord.Message, original_interaction: discord.Interaction):
            self.message = message
            self.original_interaction = original_interaction
            options = [
                discord.SelectOption(label="With next reminder", value="next_reminder"),
                # discord.SelectOption(label="After work", value="after_work"),
                discord.SelectOption(label="Custom", value="custom"),
                discord.SelectOption(label="1 hour", value="3600"),
                discord.SelectOption(label="3 hours", value="10800"),
                discord.SelectOption(label="6 hours", value="21600"),
                discord.SelectOption(label="8 hours", value="28800"),
                discord.SelectOption(label="12 hours", value="43200"),
                discord.SelectOption(label="24 hours", value="86400"),
            ]
            super().__init__(
                placeholder="Choose a duration...",
                options=options,
                custom_id="duration_select",
            )

        async def callback(self, interaction: discord.Interaction):
            assert interaction.user is not None, "Expected interaction user to be non-None"

            remind_at: datetime
            value = str(self.values[0])
            if value == "custom":
                modal = CustomSnoozeModal(self.message, self.original_interaction)
                await interaction.response.send_modal(modal)
                return  # Further handling happens in the modal callback
            elif value == "after_work":
                await interaction.response.send_message(
                    "TODO unimplemented",
                    ephemeral=True,
                )
                return
            elif value == "next_reminder":
                next_reminder = (
                    await Reminder.filter(
                        discord_user_id=interaction.user.id,
                        errored=False,
                        delivered=False,
                    )
                    .order_by("remind_at")
                    .first()
                )

                if next_reminder:
                    remind_at = next_reminder.remind_at + timedelta(seconds=1)
                else:
                    await self.original_interaction.edit_original_response(
                        content="No upcoming reminders found, please select a time manually."
                        # , view=None
                    )
                    return
            else:
                duration = int(value)
                current_utc_time = datetime.now(timezone.utc)
                remind_at = current_utc_time + timedelta(seconds=duration)

            reminder = await Reminder.create(
                discord_user_id=interaction.user.id,
                remind_at=remind_at,
                target_message_id=self.message.id,
                target_message_channel_id=self.message.channel.id,
                target_message_jump_url=self.message.jump_url,
            )
            log.info(f"New reminder created with id {reminder.id}")

            embed, view = create_reminder_embed(self.message, remind_at, "Snooze...", reminder)

            await self.original_interaction.edit_original_response(content="", embed=embed, view=view)


class SnoozeView(discord.ui.View):
    def __init__(self, message: discord.Message, original_interaction: discord.Interaction):
        super().__init__()
        self.add_item(CustomSnoozeModal.SnoozeSelect(message, original_interaction))


class Snooze(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

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
    async def quick_snooze_message(self, ctx: discord.ApplicationContext, message: discord.Message):
        current_utc_time = datetime.now(timezone.utc)
        remind_at = current_utc_time + timedelta(seconds=5)

        reminder = await Reminder.create(
            discord_user_id=ctx.author.id,
            remind_at=remind_at,
            target_message_id=message.id,
            target_message_channel_id=message.channel.id,
            target_message_jump_url=message.jump_url,
        )
        log.info(f"New reminder created with id {reminder.id}")

        embed, view = create_reminder_embed(message, remind_at, "Quick Snooze", reminder)

        await ctx.interaction.response.send_message(embed=embed, view=view, ephemeral=True)

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
    async def snooze_message(self, ctx: discord.ApplicationContext, message: discord.Message):
        snooze_view = SnoozeView(message, ctx.interaction)
        await ctx.interaction.response.send_message(
            "Choose a duration for the reminder:", view=snooze_view, ephemeral=True
        )


def setup(bot: discord.Bot):
    bot.add_cog(Snooze(bot))
