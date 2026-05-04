"""Reusable reminder UI components (buttons, modals, views)."""

from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands
from db.models.reminder import Reminder
from ezcord import log


class RescheduleModal(discord.ui.Modal):
    """Modal for rescheduling a reminder by prompting the user for a new time (or duration) in the future."""

    def __init__(self, reminder: Reminder):
        super().__init__(title="Reschedule Reminder")
        self.reminder = reminder

        self.add_item(
            discord.ui.InputText(
                label="New Duration (seconds)",
                placeholder="Enter new duration in seconds",
                required=True,
                custom_id="new_duration",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        new_duration_input: discord.ui.InputText = self.children[0]
        assert type(new_duration_input.value) is str, "Required field somehow excluded"
        new_duration = int(new_duration_input.value)

        current_utc_time = datetime.now(timezone.utc)
        new_remind_at = current_utc_time + timedelta(seconds=new_duration)

        self.reminder.remind_at = new_remind_at
        await self.reminder.save()

        timestamp = int(new_remind_at.timestamp())
        await interaction.response.send_message(
            f"Reminder ID `{self.reminder.id}` has been rescheduled for <t:{timestamp}:F> (<t:{timestamp}:R>).",
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
        self.reminder.delivered = True
        self.reminder.errored = True
        await self.reminder.save()
        await interaction.response.send_message(
            f"Reminder ID `{self.reminder.id}` for {self.reminder.target_message_jump_url} has been canceled.",
            ephemeral=False,
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
        modal = RescheduleModal(self.reminder)
        await interaction.response.send_modal(modal)


class ReminderActionView(discord.ui.View):
    """View containing reschedule and cancel buttons for a reminder."""

    def __init__(self, reminder: Reminder | None):
        super().__init__(timeout=None)
        self.reminder = reminder
        if reminder is not None:
            self.add_item(ReminderRescheduleButton(reminder))
            self.add_item(ReminderCancelButton(reminder))


class ReminderUi(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ReminderActionView(None))


def setup(bot: discord.Bot):
    bot.add_cog(ReminderUi(bot))
