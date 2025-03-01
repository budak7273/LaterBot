from datetime import datetime, timedelta, timezone

import discord
from discord.enums import IntegrationType, InteractionContextType
from discord.ext import commands
from ezcord import log

from db.models.reminder import Reminder


def create_reminder_details_embed(reminder: Reminder) -> discord.Embed:
    timestamp = int(reminder.remind_at.timestamp())
    description = (
        f"Reminder ID: {reminder.id}\n"
        f"Remind At: <t:{timestamp}:F> (<t:{timestamp}:R>)\n"
        f"Message: {reminder.target_message_jump_url}"
    )
    if reminder.delivered:
        description += "\nStatus: `Delivered`"
    elif reminder.errored:
        description += "\nStatus: `Errored`"
    else:
        description += "\nStatus: `Awaiting Delivery`"

    embed = discord.Embed(
        title="Reminder Details",
        description=description,
        color=discord.Color.blue(),
    )
    return embed


class ReminderManagement(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

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

            timestamp = int(new_remind_at.timestamp())
            await interaction.response.send_message(
                f"Reminder ID `{self.reminder.id}` has been rescheduled for <t:{timestamp}:F> (<t:{timestamp}:R>).",
                ephemeral=True,
            )

    class ReminderCancelButton(discord.ui.Button):
        def __init__(self, reminder: Reminder):
            super().__init__(
                label="Cancel",
                style=discord.ButtonStyle.danger,
                custom_id="cancel_button",
            )
            self.reminder = reminder

        async def callback(self, interaction: discord.Interaction):
            if self.reminder is None:
                await interaction.response.send_message(
                    "The Discord interaction has expired, initiate a new one to get a working button.",
                    ephemeral=True,
                )
                return
            self.reminder.errored = True
            await self.reminder.save()
            await interaction.response.send_message(
                f"Reminder ID `{self.reminder.id}` has been canceled.", ephemeral=True
            )

    class ReminderRescheduleButton(discord.ui.Button):
        def __init__(self, reminder: Reminder):
            super().__init__(
                label="Reschedule",
                style=discord.ButtonStyle.primary,
                custom_id="reschedule_button",
            )
            self.reminder = reminder

        async def callback(self, interaction: discord.Interaction):
            if self.reminder is None:
                await interaction.response.send_message(
                    "The Discord interaction has expired, initiate a new one to get a working button.",
                    ephemeral=True,
                )
                return
            modal = ReminderManagement.RescheduleModal(self.reminder)
            await interaction.response.send_modal(modal)

    class ReminderActionView(discord.ui.View):
        def __init__(self, reminder):
            super().__init__(timeout=None)
            self.reminder = reminder
            self.add_item(ReminderManagement.ReminderRescheduleButton(reminder))
            self.add_item(ReminderManagement.ReminderCancelButton(reminder))

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

            embed = create_reminder_details_embed(reminder)
            view = ReminderManagement.ReminderActionView(reminder)
            await interaction.response.send_message(
                embed=embed, view=view, ephemeral=True
            )

    class ReminderSelectView(discord.ui.View):
        def __init__(self, reminders):
            super().__init__(timeout=None)
            self.add_item(ReminderManagement.ReminderSelect(reminders))
            self.add_item(ReminderManagement.LookupByIDButton())

    class EnterReminderIDModal(discord.ui.Modal):
        def __init__(self):
            super().__init__(title="Enter Reminder ID")
            self.add_item(
                discord.ui.InputText(
                    label="Reminder ID",
                    placeholder="Enter the reminder ID",
                    required=True,
                    custom_id="reminder_id",
                )
            )

        async def callback(self, interaction: discord.Interaction):
            reminder_id_input: discord.ui.InputText = self.children[0]
            reminder_id = int(reminder_id_input.value)
            user_id = interaction.user.id

            reminder = await Reminder.get_or_none(
                id=reminder_id, discord_user_id=user_id
            )
            if reminder is None:
                await interaction.response.send_message(
                    f"No reminder found with ID {reminder_id} for your user.",
                    ephemeral=True,
                )
                return

            embed = create_reminder_details_embed(reminder)
            view = ReminderManagement.ReminderActionView(reminder)
            await interaction.response.send_message(
                embed=embed, view=view, ephemeral=True
            )

    class LookupByIDButton(discord.ui.Button):
        def __init__(self):
            super().__init__(
                label="Lookup by ID...",
                style=discord.ButtonStyle.secondary,
                custom_id="lookup_by_id_button",
            )

        async def callback(self, interaction: discord.Interaction):
            modal = ReminderManagement.EnterReminderIDModal()
            await interaction.response.send_modal(modal)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ReminderManagement.ReminderSelectView([]))
        self.bot.add_view(ReminderManagement.ReminderActionView(None))
        log.info("Registered persistent views: ReminderSelectView, ReminderActionView")

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

        view = ReminderManagement.ReminderSelectView(reminders)

        await ctx.respond(embed=embed, view=view, ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(ReminderManagement(bot))
