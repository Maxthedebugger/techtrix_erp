def calc_cost(conn, product_id):
    materials = conn.execute("""
        SELECT SUM(b.quantity * c.price)
        FROM bom_items b
        JOIN components c ON b.component_id = c.id
        WHERE b.product_id = ?
    """, (product_id,)).fetchone()[0] or 0
    labor = conn.execute("""
        SELECT SUM(pp.hours * pr.hourly_rate)
        FROM product_processes pp
        JOIN processes pr ON pp.process_id = pr.id
        WHERE pp.product_id = ?
    """, (product_id,)).fetchone()[0] or 0     
    percent = conn.execute(
        "SELECT value FROM settings WHERE key = 'overhead_percent'"
    ).fetchone()[0]
    overhead = (materials + labor) * percent / 100
    total = materials + labor + overhead
    return {"materials": materials, "labor": labor, "overhead": overhead, "total": total}