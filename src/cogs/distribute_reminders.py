import traceback
from datetime import datetime, timezone

import discord
from discord import utils
from discord.ext import commands, tasks
from ezcord import log

from db.models.reminder import Reminder


class ReminderView(discord.ui.View):
    @discord.ui.button(label="Re-snooze", style=discord.ButtonStyle.gray, emoji="🔃")
    async def button_callback(
        self, button: discord.Button, interaction: discord.Interaction
    ):
        await interaction.response.send_message(
            "You clicked the button!", ephemeral=True
        )


class ReminderDistribution(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        log.info("Starting reminder distribution loop")
        self.distribution_loop.start()

    def cog_unload(self):
        log.info("Stopping reminder distribution loop")
        self.distribution_loop.cancel()

    async def distribute_reminder(self, reminder: Reminder):
        """
        Distribute a single reminder
        """
        user: discord.Member = await utils.get_or_fetch(
            self.bot, "user", reminder.discord_user_id
        )
        log.info(f"User is {user}")
        if user is None:
            log.warning("User not found? Marking entry errored")
            reminder.errored = True
            await reminder.save()
            return

        user_dms = user.dm_channel
        if user_dms is None:
            log.info(f"User DMs for {user} not found, creating new DM channel")
            user_dms = await user.create_dm()
        log.info(str(user.dm_channel))
        if user_dms is None:
            log.warning("User DMs not found? Marking entry errored")
            reminder.errored = True
            await reminder.save()
            return

        # Bot doesn't have access to channels/messages it isn't a part of
        # channel: discord.TextChannel = await utils.get_or_fetch(
        #     self.bot, "channel", reminder.target_message_channel_id
        # )
        # if channel is None:
        #     log.warning("Channel not found? Marking entry errored and notifying user")
        #     await user_dms.send(
        #         f"Tried to remind you about Reminder ID {reminder.id} but: Channel not found"
        #     )
        #     await reminder.update(errored=True)
        #     return

        # message: discord.Message = await utils.get_or_fetch(
        #     channel,
        #     "message",
        #     reminder.target_message_id,
        # )
        # if message is None:
        #     log.warning("Message not found? Marking entry errored and notifying user")
        #     await user_dms.send(
        #         f"Tried to remind you about Reminder ID {reminder.id} but: Message not found. Was it deleted?"
        #     )
        #     await reminder.update(errored=True)
        #     return

        reminder_epoch_ms = int(reminder.remind_at.timestamp())

        embed = discord.Embed(
            title=":bell: Later™ is Now",
            description=f"You asked to be reminded about {reminder.target_message_jump_url}",
            color=discord.Color.dark_gold(),
        )
        embed.add_field(
            name="Scheduled At", value=f"<t:{reminder_epoch_ms}:F>", inline=True
        )
        embed.add_field(name=" ", value=f"<t:{reminder_epoch_ms}:R>", inline=True)
        embed.set_footer(text=f"ID: {reminder.id}")

        await user_dms.send(embed=embed, view=ReminderView())
        reminder.delivered = True
        await reminder.save()

    @tasks.loop(seconds=10.0)
    async def distribution_loop(self):

        try:
            now = datetime.now(timezone.utc)
            total_reminders = await Reminder.all().count()
            pending_delivery = Reminder.filter(
                remind_at__lte=now, errored=False, delivered=False
            ).order_by("remind_at")
            total_reminders_pending = await pending_delivery.count()

            to_deliver = await pending_delivery.first()

            if to_deliver is None:
                log.info(
                    f"No reminders to distribute yet ({total_reminders_pending} pending, {total_reminders} total in db)"
                )
                return
            log.info(
                f"Delivering reminder {to_deliver} (of {total_reminders_pending} pending)"
            )

            await self.distribute_reminder(to_deliver)

        except Exception as e:
            log.error(
                "Eating error in distribute_reminders loop (loop will continue to run)"
            )
            log.error(f"{e}\n=================================================")
            log.error(traceback.format_exc())

    @distribution_loop.before_loop
    async def before_printer(self):
        """
        Wait until the bot is ready before starting the loop
        """
        await self.bot.wait_until_ready()

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     log.info("ReminderDistribution cog loaded")


def setup(bot: discord.Bot):
    bot.add_cog(ReminderDistribution(bot))
