from tortoise import Tortoise, run_async

from db.config import TORTOISE_ORM


async def init():
    """
    Run this to set up a new database file from nothing.
    """
    await Tortoise.init(config=TORTOISE_ORM)
    # Generate the schema
    await Tortoise.generate_schemas()
    print("DB setup complete.")


if __name__ == "__main__":
    print("Running first-time DB setup...")
    run_async(init())
