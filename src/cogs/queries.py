from datetime import datetime, timedelta, timezone

import discord
from discord.enums import IntegrationType, InteractionContextType
from discord.ext import commands
from ezcord import log

from db.models.reminder import Reminder


class ReminderSelect(discord.ui.Select):
    def __init__(self, reminders):
        options = [
            discord.SelectOption(
                label=f"Reminder ID {reminder.id}", value=str(reminder.id)
            )
            for reminder in reminders
        ]
        super().__init__(
            placeholder="Select a reminder...",
            options=options,
            custom_id="reminder_select",
        )

    async def callback(self, interaction: discord.Interaction):
        reminder_id = int(self.values[0])
        reminder = await Reminder.get(id=reminder_id)

        embed = discord.Embed(
            title="Reminder Details",
            description=f"Reminder ID: {reminder.id}\n"
            f"Remind At: <t:{int(reminder.remind_at.timestamp())}:F>\n"
            f"Message: [Jump to Message]({reminder.target_message_jump_url})",
            color=discord.Color.blue(),
        )

        view = ReminderActionView(reminder)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class ReminderActionView(discord.ui.View):
    def __init__(self, reminder):
        super().__init__()
        self.reminder = reminder
        self.add_item(ReminderCancelButton(reminder))
        self.add_item(ReminderRescheduleButton(reminder))


class ReminderCancelButton(discord.ui.Button):
    def __init__(self, reminder):
        super().__init__(
            label="Cancel", style=discord.ButtonStyle.danger, custom_id="cancel_button"
        )
        self.reminder = reminder

    async def callback(self, interaction: discord.Interaction):
        self.reminder.errored = True
        await self.reminder.save()
        await interaction.response.send_message(
            f"Reminder ID {self.reminder.id} has been canceled.", ephemeral=True
        )


class ReminderRescheduleButton(discord.ui.Button):
    def __init__(self, reminder):
        super().__init__(
            label="Reschedule",
            style=discord.ButtonStyle.primary,
            custom_id="reschedule_button",
        )
        self.reminder = reminder

    async def callback(self, interaction: discord.Interaction):
        modal = RescheduleModal(self.reminder)
        await interaction.response.send_modal(modal)


class RescheduleModal(discord.ui.Modal):
    def __init__(self, reminder):
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
        new_duration = int(new_duration_input.value)

        current_utc_time = datetime.now(timezone.utc)
        new_remind_at = current_utc_time + timedelta(seconds=new_duration)

        self.reminder.remind_at = new_remind_at
        await self.reminder.save()

        await interaction.response.send_message(
            f"Reminder ID {self.reminder.id} has been rescheduled.", ephemeral=True
        )


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

        view = discord.ui.View()
        view.add_item(ReminderSelect(reminders))

        await ctx.respond(embed=embed, view=view, ephemeral=False)


def setup(bot: discord.Bot):
    bot.add_cog(Queries(bot))
