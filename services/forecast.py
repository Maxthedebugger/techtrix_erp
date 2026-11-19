import math
from sklearn.linear_model import LinearRegression


def forecast_component(conn, component_id):
    rows = conn.execute(
        """SELECT julianday('now') - julianday(created_at) AS days_ago, -change AS used
           FROM stock_movements
           WHERE component_id = ? AND reason = 'production'
             AND created_at >= datetime('now', '-90 days')
           ORDER BY created_at""",
        (component_id,),
    ).fetchall()
    if len(rows) < 2:
        return None

    x = []
    y = []
    total = 0
    for r in rows:
        total = total + r["used"]
        x.append([-r["days_ago"]])
        y.append(total)

    model = LinearRegression()
    model.fit(x, y)
    per_day = model.coef_[0]
    if per_day <= 0:
        return None

    comp = conn.execute("SELECT * FROM components WHERE id = ?", (component_id,)).fetchone()
    days_left = comp["quantity"] / per_day
    order_qty = math.ceil(per_day * 30)
    return {"per_day": per_day, "days_left": days_left, "order_qty": order_qty}