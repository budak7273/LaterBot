import datetime

from tortoise import fields, models


class User(models.Model):
    """
    Represents a user with their preferences and settings.
    """

    id = fields.IntField(primary_key=True)
    """Bot's unique ID for the user"""

    discord_user_id = fields.BigIntField(unique=True)
    """Discord user ID of the user"""

    timezone_offset = fields.IntField(default=0)
    """User's timezone offset from UTC in minutes"""

    work_end_time = fields.TimeDeltaField(default=datetime.timedelta(seconds=0))
    """Time of day when the user's work ends. Must combine with timezone_offset for a meaningful timestamp."""

    def __str__(self):
        return f"<User {self.discord_user_id} (UTC offset: {self.timezone_offset}) (Work end offset: {self.work_end_time})>"

    @classmethod
    async def get_or_create_from_discord_user_id(cls, discord_user_id: int):
        user, created = await cls.get_or_create(
            discord_user_id=discord_user_id,
            defaults={
                "timezone_offset": 0,
                "work_end_time": datetime.timedelta(hours=17),  # Default to 5 PM
            },
        )
        return user, created

    class Meta:
        table = "users"
