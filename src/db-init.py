from tortoise import Tortoise, run_async


async def init():
    """
    Run this to set up a new database file from nothing.
    """
    await Tortoise.init(
        db_url="sqlite://laterbot-tortoise.sqlite3",
        modules={"models": ["db.models.reminder"]},
    )
    # Generate the schema
    await Tortoise.generate_schemas()
    print("DB setup complete.")


if __name__ == "__main__":
    print("Running first-time DB setup...")
    run_async(init())
