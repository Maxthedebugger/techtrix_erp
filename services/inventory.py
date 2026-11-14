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