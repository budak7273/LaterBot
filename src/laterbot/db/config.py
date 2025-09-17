from copy import deepcopy
from typing import Any

TORTOISE_ORM: dict[str, Any] = {
    "connections": {
        "default": "sqlite://data/laterbot-tortoise.sqlite3",
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

# The bot has to look up-and-out from its src folder to find sqlite file
TORTOISE_ORM_FOR_BOT = deepcopy(TORTOISE_ORM)
TORTOISE_ORM_FOR_BOT["connections"][
    "default"
] = "sqlite://../../data/laterbot-tortoise.sqlite3"
