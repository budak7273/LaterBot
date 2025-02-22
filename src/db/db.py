import ezcord


class ReminderDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("laterbot.db")

    async def setup(self):
        """Execute a single query."""
        await self.exec(
            """ -- beginsql
            CREATE TABLE IF NOT EXISTS reminders(
            requesting_user_id INTEGER PRIMARY KEY,
            coins INTEGER DEFAULT 0
            )
            -- endsql
            """
        )

    async def add_coins(self, requesting_user_id, amount):
        """Execute multiple queries in one connection."""
        async with self.start() as cursor:
            await cursor.exec(
                """ -- beginsql
                INSERT OR IGNORE INTO reminders (requesting_user_id) VALUES (?)
                -- endsql
                """,
                (requesting_user_id,),
            )
            await cursor.exec(
                """ --beginsql
                UPDATE reminders SET coins = coins + ? WHERE requesting_user_id = ?
                -- endsql
                """,
                (amount, requesting_user_id),
            )

    async def get_users(self):
        """Return all result rows."""
        return await self.all(
            """ --beginsql
            SELECT * FROM reminders
            -- endsql
            """
        )

    async def get_one_user(self, requesting_user_id):
        """Return one result row."""
        return await self.one(
            """
            --beginsql
            SELECT * FROM reminders WHERE requesting_user_id = ?
            -- endsql
            """,
            (requesting_user_id,),
        )


print("Setting up database...")

db = ReminderDB()

print("Database started.")
