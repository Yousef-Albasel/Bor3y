import aiosqlite
from datetime import datetime

DB_PATH = "reminders.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                when_utc TEXT NOT NULL
            )
        """)
        await db.commit()

async def add_reminder(user_id, channel_id, message, when_utc):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO reminders (user_id, channel_id, message, when_utc) VALUES (?, ?, ?, ?)",
            (user_id, channel_id, message, when_utc)
        )
        await db.commit()

async def get_due_reminders(now_utc):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, user_id, channel_id, message, when_utc FROM reminders WHERE when_utc <= ?",
            (now_utc,)
        )
        return await cursor.fetchall()

async def delete_reminder(reminder_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        await db.commit()