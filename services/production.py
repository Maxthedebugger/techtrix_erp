def start_production(conn, order_id):
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        raise ValueError("Няма такава поръчка")
    if order["status"] != "new":
        raise ValueError("Само нова поръчка може да влезе в производство")
    if order["status"] != "new":
        raise ValueError("Само нова поръчка може да влезе в производство")
    needs = conn.execute("""
        SELECT c.id, c.part_number, c.quantity AS in_stock, b.quantity * ? AS needed
        FROM bom_items b
        JOIN components c ON b.component_id = c.id
        WHERE b.product_id = ?
    """, (order["quantity"], order["product_id"])).fetchall()
    missing = []
    for n in needs:
        if n["in_stock"] < n["needed"]:
            missing.append(f'{n["part_number"]} (нужни {n["needed"]}, има {n["in_stock"]})')
    if missing:
        raise ValueError("Не достигат: " + ", ".join(missing))
    with conn:
        for n in needs:
            conn.execute("UPDATE components SET quantity = quantity - ? WHERE id = ?", (n["needed"],n["id"]))   
            conn.execute(
                "INSERT INTO stock_movements (component_id, change, reason, order_id) VALUES (?, ?, 'production', ?)",
                (n["id"], -n["needed"], order_id)
            )
        conn.execute("UPDATE orders SET status = 'in_production' WHERE id = ?", (order_id,))

def finish_order(conn, order_id):
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        raise ValueError("Няма такава поръчка")
    if order["status"] != "in_production":
        raise ValueError("Само поръчка в производство може да стане готова")
    with conn:
        conn.execute("UPDATE products SET quantity = quantity + ? WHERE id = ?", (order["quantity"], order["product_id"]))
        conn.execute(
            "INSERT INTO product_movements (product_id, change, reason, order_id) VALUES (?, ?, 'production', ?)",
            (order["product_id"], order["quantity"], order_id)
        )
        conn.execute("UPDATE orders SET status = 'done' WHERE id = ?", (order_id,))


def cancel_order(conn, order_id):
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        raise ValueError("Няма такава поръчка")
    if order["status"] != "new":
        raise ValueError("Само нова поръчка може да се откаже")
    with conn:
        conn.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))