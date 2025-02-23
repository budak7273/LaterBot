from tortoise import fields, models


class Reminder(models.Model):
    """
    Represents a reminder that the bot will send to a user at a certain time.
    """

    id = fields.IntField(primary_key=True)
    discord_user_id = fields.BigIntField()
    remind_at = fields.DatetimeField()
    discord_message_id = fields.BigIntField()

    # def __str__(self):
    #     return self.name

    class Meta:
        table = "reminders"
