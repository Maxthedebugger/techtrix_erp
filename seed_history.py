import random
from database import get_db

random.seed(42)
conn = get_db()

bom = conn.execute("SELECT product_id, component_id, quantity FROM bom_items").fetchall()

with conn:
    for days_ago in range(90, 0, -1):
        for product_id in [1, 2, 3]:
            made = random.randint(0, 4)
            if made == 0:
                continue
            for b in bom:
                if b["product_id"] == product_id:
                    conn.execute(
                        "INSERT INTO stock_movements (component_id, change, reason, created_at) "
                        "VALUES (?, ?, 'production', datetime('now', ?))",
                        (b["component_id"], -b["quantity"] * made, f"-{days_ago} days"),
                    )
conn.close()
print("Готово: историята е добавена")