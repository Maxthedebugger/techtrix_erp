from services.forecast import forecast_component
 
 
def get_dashboard(conn):
    """Събира всички статистики за началната страница в един речник (dict)."""
    d = {}
 
    # 1) Компоненти под минимума
    d["low"] = conn.execute(
        """SELECT part_number, quantity, min_quantity FROM components
           WHERE active = 1 AND quantity < min_quantity
           ORDER BY part_number"""
    ).fetchall()
 
    # 2) Компоненти, които по AI прогнозата ще свършат до 7 дни
    soon = []
    components = conn.execute(
        "SELECT id, part_number FROM components WHERE active = 1"
    ).fetchall()
    for c in components:
        f = forecast_component(conn, c["id"])
        if f is not None and f["days_left"] <= 7:
            soon.append({"part_number": c["part_number"], "days": int(f["days_left"])})
    soon.sort(key=lambda s: s["days"])
    d["soon"] = soon
 
    # 3) Поръчки по статус
    counts = {"new": 0, "in_production": 0, "done": 0}
    for r in conn.execute("SELECT status, COUNT(*) AS n FROM orders GROUP BY status"):
        if r["status"] in counts:
            counts[r["status"]] = r["n"]
    d["orders"] = counts
 
    # 4) Продажби този месец (по датата на изпращане)
    month = conn.execute(
        """SELECT COUNT(*) AS n, COALESCE(SUM(s.quantity * p.sale_price), 0) AS revenue
           FROM product_movements pm
           JOIN sales s ON pm.sale_id = s.id
           JOIN products p ON s.product_id = p.id
           WHERE pm.reason = 'shipment'
             AND pm.created_at >= date('now', 'start of month')"""
    ).fetchone()
    d["month_sales"] = month["n"]
    d["month_revenue"] = month["revenue"]
 
    # 5) Колко броя от всеки продукт можем да произведем с наличните части
    d["can_make"] = conn.execute(
        """SELECT p.code, MIN(c.quantity / b.quantity) AS n
           FROM bom_items b
           JOIN components c ON b.component_id = c.id
           JOIN products p ON b.product_id = p.id
           WHERE p.active = 1
           GROUP BY p.id
           ORDER BY p.code"""
    ).fetchall()
 
    # 6) Стойност на склада
    d["stock_value"] = conn.execute(
        "SELECT COALESCE(SUM(quantity * price), 0) FROM components WHERE active = 1"
    ).fetchone()[0]
 
    # 7) Последните 10 движения (компоненти и продукти заедно)
    d["last_moves"] = conn.execute(
        """SELECT sm.created_at, c.part_number AS code, 'компонент' AS kind, sm.change, sm.reason
           FROM stock_movements sm JOIN components c ON sm.component_id = c.id
           UNION ALL
           SELECT pm.created_at, p.code, 'продукт', pm.change, pm.reason
           FROM product_movements pm JOIN products p ON pm.product_id = p.id
           ORDER BY created_at DESC
           LIMIT 10"""
    ).fetchall()
 
    # 8) Продукти без продажба последните 30 дни
    d["no_sales"] = conn.execute(
        """SELECT p.code, p.name,
                  (SELECT MAX(pm.created_at) FROM product_movements pm
                   WHERE pm.product_id = p.id AND pm.reason = 'shipment') AS last_sale
           FROM products p
           WHERE p.active = 1
             AND NOT EXISTS (SELECT 1 FROM product_movements pm
                             WHERE pm.product_id = p.id AND pm.reason = 'shipment'
                               AND pm.created_at >= datetime('now', '-30 days'))
           ORDER BY p.code"""
    ).fetchall()
 
    # 9) Топ 3 продукта за месеца
    d["top"] = conn.execute(
        """SELECT p.code, p.name, SUM(-pm.change) AS sold
           FROM product_movements pm JOIN products p ON pm.product_id = p.id
           WHERE pm.reason = 'shipment'
             AND pm.created_at >= date('now', 'start of month')
           GROUP BY p.id
           ORDER BY sold DESC
           LIMIT 3"""
    ).fetchall()
 
    # 10) Чакащи продажби (още не са изпратени) и дали има достатъчно на склад
    d["pending"] = conn.execute(
        """SELECT s.id, s.customer, p.code, s.quantity, p.quantity AS in_stock
           FROM sales s JOIN products p ON s.product_id = p.id
           WHERE s.status = 'new'
           ORDER BY s.created_at"""
    ).fetchall()
 
    return d
Branded Links & QR Codes for Growth | s.id
Launch branded short links, campaign microsites, and dynamic QR codes from one platform. Built for marketing, growth, SaaS, and AI teams.
 
