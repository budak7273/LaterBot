from tortoise import fields, models


class Reminder(models.Model):
    """
    Represents a reminder that the bot will send to a user at a certain time.
    """

    id = fields.IntField(primary_key=True)
    """Bot's unique ID for the reminder"""

    discord_user_id = fields.BigIntField()
    """Discord user ID of the user who requested the reminder"""

    remind_at = fields.DatetimeField()
    """When the user requested that reminder be sent (UTC time)"""

    target_message_id = fields.BigIntField()
    """Discord message ID of the message the user wants to be reminded about"""

    target_message_jump_url = fields.TextField()
    """URL to jump to the message the user wants to be reminded about"""

    target_message_channel_id = fields.BigIntField()
    """Discord channel ID of the message the user wants to be reminded about (must be retained to look up discord message object). Bot may not have access."""

    errored = fields.BooleanField(default=False)
    """Whether the reminder errored when trying to send it (record kept around for troubleshooting, but won't try to send again)"""

    delivered = fields.BooleanField(default=False)
    """Whether the reminder has been successfully delivered to the user"""

    # TODO auto-delete delivered messages N days after completion?

    def __str__(self):
        return f"<Reminder at {self.remind_at} for message {self.target_message_id}>"

    class Meta:
        table = "reminders"
