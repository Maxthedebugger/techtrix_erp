def set_bom_item(conn, product_id, component_id, quantity):
    existing = conn.execute(
        "SELECT id FROM bom_items WHERE product_id = ? AND component_id = ?",
        (product_id, component_id)
    ).fetchone()
    with conn:
        if quantity == 0:
            conn.execute("DELETE FROM bom_items WHERE product_id = ? AND component_id = ?", (product_id,component_id))   
        elif existing:
            conn.execute("UPDATE bom_items SET quantity = ? WHERE id = ?", (quantity, existing["id"]))
        else:
            conn.execute("INSERT INTO bom_items (product_id, component_id, quantity) VALUES (?, ?, ?)", (product_id, component_id, quantity))