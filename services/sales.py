def ship_sale(conn, sale_id):
    sale = conn.execute("SELECT * FROM sales WHERE id = ?", (sale_id,)).fetchone()
    if sale is None:
        raise ValueError("Няма такава продажба")
    if sale["status"] != "new":
        raise ValueError("Само нова продажба може да се изпрати")
    product = conn.execute("SELECT * FROM products WHERE id = ?", (sale["product_id"],)).fetchone()
    if product["quantity"] < sale["quantity"]:
        raise ValueError(f"Няма достатъчно {product['code']}: на склад {product['quantity']}, нужни {sale['quantity']}")
    with conn:
        conn.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (sale["quantity"], sale["product_id"]))
        conn.execute(
            "INSERT INTO product_movements (product_id, change, reason, sale_id) VALUES (?, ?, 'shipment', ?)",
            (sale["product_id"], -sale["quantity"], sale_id),
        )
        conn.execute("UPDATE sales SET status = 'shipped' WHERE id = ?", (sale_id,))


def cancel_sale(conn, sale_id):
    sale = conn.execute("SELECT * FROM sales WHERE id = ?", (sale_id,)).fetchone()
    if sale is None:
        raise ValueError("Няма такава продажба")
    if sale["status"] != "new":
        raise ValueError("Само нова продажба може да се откаже")
    with conn:
        conn.execute("UPDATE sales SET status = 'cancelled' WHERE id = ?", (sale_id,))