# Notes

Aerich was set up via `aerich init -t db.config.TORTOISE_ORM -s src/laterbot` from the root directory.

Needed special aerich build to fix bug <https://github.com/tortoise/aerich/issues/63#issuecomment-2848841380>

Manually brought stuff over from pre-aerich via: <https://stackoverflow.com/a/2359280>

```sqlite
ATTACH DATABASE "laterbot-tortoise-BKUP.sqlite3" AS "BKUP";
ATTACH DATABASE "laterbot-tortoise.sqlite3" AS "NEW";
INSERT INTO NEW.reminders SELECT * FROM BKUP.reminders;
```
