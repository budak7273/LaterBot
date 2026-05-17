"""Reusable reminder UI components (buttons, modals, views)."""

from datetime import datetime, timezone
from typing import Tuple

import dateparser
import discord
from discord.ext import commands
from discord.ui import View
from db.models.reminder import Reminder
from ezcord import log


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
    embed.set_footer(text=f"{footer_text} | ID: {reminder.id}")

    view = ReminderUi.ReminderActionView(reminder)

    return embed, view


async def verify_reminder_still_open(reminder: Reminder, interaction: discord.Interaction) -> bool:
    await reminder.refresh_from_db(fields=["delivered", "errored"])
    if reminder.delivered:
        await interaction.response.send_message(
            f"Reminder ID `{reminder.id}` has already been delivered or canceled, it cannot be rescheduled.",
            ephemeral=True,
        )
        return False
    elif reminder.errored:
        await interaction.response.send_message(
            f"Reminder ID `{reminder.id}` has errored and cannot be rescheduled. Please create a new reminder.",
            ephemeral=True,
        )
        return False
    return True


class ReminderUi(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    class CustomSnoozeModal(discord.ui.Modal):
        """Modal for custom snooze duration input. Handles both creating new reminders (snooze) and updating existing ones (reschedule)."""

        def __init__(self, target: discord.Message | Reminder, original_interaction: discord.Interaction | None = None):
            if isinstance(target, Reminder):
                title = "Reschedule Reminder"
            else:
                title = "Custom Snooze Duration"

            super().__init__(title=title)

            self.target = target
            self.original_interaction = original_interaction

            self.add_item(
                discord.ui.InputText(
                    label="Custom Duration",
                    placeholder="e.g., '2 hours', 'tomorrow at 3pm', '30 minutes', 'in 1 day'",
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
                parsed_datetime = dateparser.parse(
                    user_input,
                    settings={
                        "RETURN_AS_TIMEZONE_AWARE": True,
                        "PREFER_DATES_FROM": "future",
                        # TODO factor in user's timezone
                        "RELATIVE_BASE": current_utc_time,
                    },
                )

                log.info(
                    f"Parsed datetime: {parsed_datetime} ({repr(parsed_datetime)}) from user input: '{user_input}'"
                )

                if parsed_datetime is None:
                    await interaction.response.send_message(
                        f"Could not parse '`{user_input}`'. Please try formats like '2 hours', 'tomorrow at 3pm', or '30 minutes'.",
                        ephemeral=True,
                    )
                    return

                if parsed_datetime.tzinfo is None:
                    # TODO can this case happen? given Timezone Ware is enabled
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

            # Handle creating new reminder (snooze) vs updating existing (reschedule)
            if isinstance(self.target, discord.Message):
                # Snooze case: create new reminder
                assert self.original_interaction is not None, "original_interaction must be provided for snooze"
                reminder = await Reminder.create(
                    discord_user_id=interaction.user.id,
                    remind_at=remind_at,
                    target_message_id=self.target.id,
                    target_message_channel_id=self.target.channel.id,
                    target_message_jump_url=self.target.jump_url,
                )
                log.info(f"New reminder created with id {reminder.id}")

                embed, view = create_reminder_embed(self.target, remind_at, "Snooze...", reminder)

                await self.original_interaction.edit_original_response(content="", embed=embed, view=view)
                await interaction.response.defer(invisible=True)
            elif isinstance(self.target, Reminder):
                self.target.remind_at = remind_at
                await self.target.save()

                timestamp = int(remind_at.timestamp())
                await interaction.response.send_message(
                    f"Reminder ID `{self.target.id}` has been rescheduled for <t:{timestamp}:F> (<t:{timestamp}:R>).",
                    ephemeral=True,
                )

    class ReminderCancelButton(discord.ui.Button):
        """Button to cancel a reminder."""

        # can be None if interaction has expired
        reminder: Reminder | None

        def __init__(self, reminder: Reminder):
            super().__init__(
                label="Cancel",
                style=discord.ButtonStyle.danger,
                custom_id="cancel_button",
                emoji=discord.PartialEmoji(name="🗑️"),
            )
            self.reminder = reminder

        async def callback(self, interaction: discord.Interaction):
            if self.reminder is None:
                await interaction.response.send_message(
                    "The Discord interaction has expired, initiate a new one to get a working button.",
                    ephemeral=True,
                )
                return

            if not await verify_reminder_still_open(self.reminder, interaction):
                return

            self.reminder.delivered = True
            await self.reminder.save()
            is_private_dm = isinstance(interaction.channel, discord.DMChannel)
            await interaction.response.send_message(
                f"Reminder ID `{self.reminder.id}` for {self.reminder.target_message_jump_url} has been canceled.",
                ephemeral=not is_private_dm,
            )

    class ReminderRescheduleButton(discord.ui.Button):
        """Button to reschedule a reminder via modal."""

        # can be None if interaction has expired
        reminder: Reminder | None

        def __init__(self, reminder: Reminder):
            super().__init__(
                label="Reschedule",
                style=discord.ButtonStyle.primary,
                custom_id="reschedule_button",
                emoji=discord.PartialEmoji(name="🗓"),
            )
            self.reminder = reminder

        async def callback(self, interaction: discord.Interaction):
            if self.reminder is None:
                await interaction.response.send_message(
                    "The Discord interaction has expired, initiate a new one to get a working button.",
                    ephemeral=True,
                )
                return

            if not await verify_reminder_still_open(self.reminder, interaction):
                return

            modal = ReminderUi.CustomSnoozeModal(self.reminder)
            await interaction.response.send_modal(modal)

    class ReminderActionView(discord.ui.View):
        """View containing reschedule and cancel buttons for a reminder."""

        def __init__(self, reminder: Reminder | None):
            super().__init__(timeout=None)
            self.reminder = reminder
            if reminder is not None:
                self.add_item(ReminderUi.ReminderRescheduleButton(reminder))
                self.add_item(ReminderUi.ReminderCancelButton(reminder))

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ReminderUi.ReminderActionView(None))


def setup(bot: discord.Bot):
    bot.add_cog(ReminderUi(bot))
