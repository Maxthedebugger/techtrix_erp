def add_product(conn, code, name, sale_price):
    code = code.strip().upper()
    if code == "" or name.strip() == "":
        raise ValueError("Кодът и името са задължителни")
    if sale_price <= 0:
        raise ValueError("Цената трябва да е по-голяма от 0")
    existing = conn.execute("SELECT id FROM products WHERE code = ?", (code,)).fetchone()
    if existing is not None:
        raise ValueError("Вече има продукт с код " + code)
    with conn:
        cur = conn.execute(
            "INSERT INTO products (code, name, quantity, sale_price) VALUES (?, ?, 0, ?)",
            (code, name.strip(), sale_price),
        )
    return cur.lastrowid


def remove_product(conn, product_id):
    product = conn.execute("SELECT * FROM products WHERE id = ? AND active = 1", (product_id,)).fetchone()
    if product is None:
        raise ValueError("Няма такъв продукт")
    with conn:
        conn.execute("UPDATE orders SET status = 'cancelled' WHERE product_id = ? AND status = 'new'", (product_id,))
        conn.execute("UPDATE sales SET status = 'cancelled' WHERE product_id = ? AND status = 'new'", (product_id,))
        conn.execute("UPDATE products SET active = 0 WHERE id = ?", (product_id,))