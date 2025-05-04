from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "work_end_time";
        ALTER TABLE "users" ADD "work_end_time" BIGINT NOT NULL DEFAULT 0;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "work_end_time";
        ALTER TABLE "users" ADD "work_end_time" TIME NOT NULL DEFAULT 0;
        """
