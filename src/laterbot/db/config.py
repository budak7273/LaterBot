TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://laterbot-tortoise.sqlite3",
    },
    "apps": {
        "models": {
            "models": [
                "aerich.models",
                "db.models.reminder",
                "db.models.user",
            ],
            "default_connection": "default",
        },
    },
}

# Make aerich generate the database in the project root, but the bot has to look ip from its src folder to find it
TORTOISE_ORM_FOR_BOT = TORTOISE_ORM.copy()
TORTOISE_ORM_FOR_BOT["connections"][
    "default"
] = "sqlite://../../laterbot-tortoise.sqlite3"
