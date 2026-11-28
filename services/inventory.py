def receive_delivery(conn, component_id, qty, unit_price):
    comp = conn.execute(
        "SELECT quantity, price FROM components WHERE id = ?", (component_id,)
    ).fetchone()
    old_qty = comp["quantity"]
    old_price = comp["price"] or 0
    new_qty = old_qty + qty
    new_price = ( old_qty * old_price + qty*unit_price)/new_qty
    with conn:
        conn.execute(
        "UPDATE components SET quantity = ?, price = ? WHERE id = ?",
        (new_qty, new_price, component_id)
        )
        conn.execute(
            "INSERT INTO stock_movements (component_id, change, unit_price, reason) VALUES (?, ?, ?, 'delivery')",
            (component_id, qty, unit_price)
        )
def correct_stock(conn, component_id, change):
    comp = conn.execute(
        "SELECT quantity FROM components WHERE id = ?", (component_id,)
    ).fetchone()
    new_qty = comp["quantity"] + change
    if new_qty < 0:
        raise ValueError("Количеството не може да стане отрицателно")
    with conn:
        conn.execute("UPDATE components SET quantity = ?  WHERE id = ?", (new_qty, component_id))
        conn.execute("INSERT INTO stock_movements (component_id, change, reason) VALUES (?, ?, 'correction')", (component_id, change))
def add_component(conn, part_number, name, type, min_quantity, supplier):
    part_number = part_number.strip().upper()
    if part_number == "" or name.strip() == "":
        raise ValueError("Кодът и името са задължителни")
    existing = conn.execute("SELECT id FROM components WHERE part_number = ?", (part_number,)).fetchone()
    if existing is not None:
        raise ValueError("Вече има компонент с код " + part_number)
    with conn:
        conn.execute(
            "INSERT INTO components (part_number, name, type, quantity, min_quantity, price, supplier) "
            "VALUES (?, ?, ?, 0, ?, 0, ?)",
            (part_number, name.strip(), type, min_quantity, supplier),
        )


def remove_component(conn, component_id):
    comp = conn.execute("SELECT * FROM components WHERE id = ? AND active = 1", (component_id,)).fetchone()
    if comp is None:
        raise ValueError("Няма такъв компонент")
    with conn:
        conn.execute("DELETE FROM bom_items WHERE component_id = ?", (component_id,))
        conn.execute("UPDATE components SET active = 0 WHERE id = ?", (component_id,))

def receive_delivery_many(conn, items):
    """Заприхождава много компоненти наведнъж.
    items е списък от (код, количество, цена). Първо проверява ВСИЧКИ редове,
    и само ако всички са наред, записва всичко в една транзакция."""
    if len(items) == 0:
        raise ValueError("Добавете поне един компонент")
    checked = []
    for code, qty, unit_price in items:
        code = code.strip().upper()
        comp = conn.execute(
            "SELECT id FROM components WHERE part_number = ? AND active = 1", (code,)
        ).fetchone()
        if comp is None:
            raise ValueError(f"Няма компонент с код „{code}“")
        if qty <= 0:
            raise ValueError(f"Количеството за „{code}“ трябва да е поне 1")
        if unit_price < 0:
            raise ValueError(f"Цената за „{code}“ не може да е отрицателна")
        checked.append((comp["id"], qty, unit_price))
    with conn:
        for component_id, qty, unit_price in checked:
            comp = conn.execute(
                "SELECT quantity, price FROM components WHERE id = ?", (component_id,)
            ).fetchone()
            old_qty = comp["quantity"]
            old_price = comp["price"] or 0
            new_qty = old_qty + qty
            new_price = (old_qty * old_price + qty * unit_price) / new_qty
            conn.execute(
                "UPDATE components SET quantity = ?, price = ? WHERE id = ?",
                (new_qty, new_price, component_id),
            )
            conn.execute(
                "INSERT INTO stock_movements (component_id, change, unit_price, reason) VALUES (?, ?, ?, 'delivery')",
                (component_id, qty, unit_price),
            )
    return len(checked)