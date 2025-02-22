from datetime import datetime, timedelta, timezone

import discord
from discord.enums import IntegrationType, InteractionContextType
from discord.ext import commands


class Snooze(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    # @commands.user_command(
    #     name="Remind me about this user",
    #     contexts={
    #         InteractionContextType.bot_dm,
    #         InteractionContextType.private_channel,
    #         InteractionContextType.guild,
    #     },
    #     integration_types={IntegrationType.guild_install, IntegrationType.user_install},
    # )
    # async def remind_user(
    #     self, ctx: discord.ApplicationContext, member: discord.Member
    # ):
    #     await ctx.respond(f"{ctx.author.mention} snoozing {member.mention}!")

    async def real_quick_snooze_message(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ):
        current_utc_time = datetime.now(timezone.utc)
        remind_at = current_utc_time + timedelta(hours=6)

        epoch_timestamp = int(remind_at.timestamp())
        embed = discord.Embed(
            title=":white_check_mark: Reminding you Later™",
            description=f"Got it - you'll be reminded about {message.jump_url} <t:{epoch_timestamp}:R> (<t:{epoch_timestamp}:F>)!",
            color=discord.Color.green(),
        )
        embed.set_footer(text="Quick Snooze")

        await ctx.respond(embed=embed)

    @commands.message_command(
        name="Quiz Snooze",
        contexts={
            InteractionContextType.bot_dm,
            InteractionContextType.private_channel,
            InteractionContextType.guild,
        },
        integration_types={IntegrationType.guild_install, IntegrationType.user_install},
    )
    async def quick_snooze_message(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ):
        await self.real_quick_snooze_message(ctx, message)

    # @commands.message_command(
    #     name="DEBUG Quiz Snooze",
    #     guild_ids=[1267160007854784633],
    # )
    # async def debug_quick_snooze_message(
    #     self, ctx: discord.ApplicationContext, message: discord.Message
    # ):
    #     await self.real_quick_snooze_message(ctx, message)


def setup(bot: discord.Bot):
    bot.add_cog(Snooze(bot))
