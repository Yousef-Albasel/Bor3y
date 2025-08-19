import aiosqlite

DB_PATH = "tasks.db"

async def init_task_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assigner_id INTEGER NOT NULL,
                assignee_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                task TEXT NOT NULL
            )
        """)
        await db.commit()

async def add_task(assigner_id, assignee_id, channel_id, task):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO tasks (assigner_id, assignee_id, channel_id, task) VALUES (?, ?, ?, ?)",
            (assigner_id, assignee_id, channel_id, task)
        )
        await db.commit()

async def delete_task(task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await db.commit()

async def get_all_tasks():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, assigner_id, assignee_id, channel_id, task FROM tasks"
        )
        return await cursor.fetchall()