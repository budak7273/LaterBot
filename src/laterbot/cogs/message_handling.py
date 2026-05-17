import discord
from discord.ext import commands
from ezcord import log


class MessageHandling(commands.Cog):
    """Handles non-command message interactions"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event: discord.RawReactionActionEvent):
        """Delete the message if reacted with ❌ emoji. Only works in user DM channels right now (the only place non-ephemeral messages are sent)"""

        assert self.bot.user is not None, "Bot user not logged in?"

        if event.emoji.name != "❌":
            return

        try:
            reacting_user = await self.bot.get_or_fetch_user(event.user_id)
            assert reacting_user is not None, f"Could not find user {event.user_id}"

            user_dms = reacting_user.dm_channel
            if user_dms is None:
                log.info(f"User DMs for {reacting_user} not found, creating new DM channel")
                user_dms = await reacting_user.create_dm()
            assert user_dms is not None, f"Reaction response: Failed to open DMs with User {reacting_user}"

            assert (
                user_dms.id == event.channel_id
            ), f"Channel mismatch between reacting user DMs id of {user_dms.id} and and event id {event.channel_id}. Event info: {event}"

            message = await user_dms.fetch_message(event.message_id)
            assert message is not None, f"Could not find message {event.message_id}"

            # Only work on messages the bot itself has sent (even though it shouldn't ever trigger on another message)
            if message.author.id != self.bot.user.id:
                return

            await message.delete()
            log.info(f"Deleted message {message.id} due to ❌ reaction from user {reacting_user}")
        except discord.HTTPException as e:
            raise Exception(f"Failed to reaction response delete message {event.message_id}: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(MessageHandling(bot))
