from tortoise import fields, models


class User(models.Model):
    """
    Represents a user with their preferences and settings.
    """

    id = fields.IntField(primary_key=True)
    """Bot's unique ID for the user"""

    discord_user_id = fields.BigIntField(unique=True)
    """Discord user ID of the user"""

    timezone_offset = fields.IntField()
    """User's timezone offset from UTC in minutes"""

    work_end_time = fields.TimeField()
    """Time of day (in HH:MM:SS format) when the user's work ends"""

    def __str__(self):
        return f"<User {self.discord_user_id} (UTC offset: {self.timezone_offset})>"

    class Meta:
        table = "users"
