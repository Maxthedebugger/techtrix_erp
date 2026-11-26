# Добавя новата таблица login_log в съществуваща база, без да трие данните.
# Пуска се веднъж: python migrate.py
from database import get_db

conn = get_db()
conn.execute("""
    CREATE TABLE IF NOT EXISTS login_log (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        success INTEGER NOT NULL,
        login_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_seen TEXT DEFAULT CURRENT_TIMESTAMP,
        logout_at TEXT
    )
""")
conn.commit()
conn.close()
print("Готово: таблицата login_log е налична")