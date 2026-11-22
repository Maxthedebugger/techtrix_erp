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