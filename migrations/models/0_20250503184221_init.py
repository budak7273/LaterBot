from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);
CREATE TABLE "reminders" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "discord_user_id" BIGINT NOT NULL,
    "remind_at" TIMESTAMP NOT NULL,
    "target_message_id" BIGINT NOT NULL,
    "target_message_jump_url" TEXT NOT NULL,
    "target_message_channel_id" BIGINT NOT NULL,
    "errored" INT NOT NULL DEFAULT 0,
    "delivered" INT NOT NULL DEFAULT 0
) /* Represents a reminder that the bot will send to a user at a certain time. */;
CREATE TABLE "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "discord_user_id" BIGINT NOT NULL UNIQUE,
    "timezone_offset" INT NOT NULL,
    "work_end_time" TIME NOT NULL
) /* Represents a user with their preferences and settings. */;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
