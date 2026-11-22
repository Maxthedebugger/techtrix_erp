from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db
from services.inventory import receive_delivery, correct_stock
from services.costing import calc_cost
from services.recipes import set_bom_item
from services.production import start_production, finish_order, cancel_order
from services.forecast import forecast_component
from services.sales import ship_sale, cancel_sale

app = Flask(__name__)

app.secret_key = "techtrix-dev-key-2026"
def require_role(*roles):
    if "username" not in session:
        return redirect(url_for("login"))
    if roles and session["role"] not in roles:
        return "Нямате достъп до тази страница", 403
    return None

@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("index"))
        return "Грешно име или парола"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
@app.route("/components")
def components():
    denied = require_role("director", "warehouse")
    if denied:
        return denied
    conn = get_db()
    rows = conn.execute("SELECT * FROM components ORDER BY part_number").fetchall()
    conn.close()
    return render_template("components.html", components=rows)
@app.route("/delivery", methods=["GET", "POST"])
def delivery():
    denied = require_role("director", "warehouse")
    if denied:
        return denied
    conn = get_db()
    if request.method == "POST":
        component_id = int(request.form["component_id"])
        qty = int(request.form["qty"])
        unit_price = float(request.form["unit_price"])
        receive_delivery(conn, component_id, qty, unit_price)
        conn.close()
        return redirect(url_for("components"))
    rows = conn.execute("SELECT id, part_number, name FROM components ORDER BY part_number").fetchall()
    conn.close()
    return render_template("delivery.html", components=rows)
@app.route("/movements")
def movements():
    denied = require_role("director", "warehouse")
    if denied:
        return denied
    conn = get_db()
    rows = conn.execute(
        """SELECT m.created_at, c.part_number, c.name, m.change, m.unit_price, m.reason
           FROM stock_movements m
           JOIN components c ON c.id = m.component_id
           ORDER BY m.id DESC"""
    ).fetchall()
    moves = conn.execute(
        """SELECT m.created_at, p.code, m.change, m.reason, m.order_id
           FROM product_movements m
           JOIN products p ON p.id = m.product_id
           ORDER BY m.id DESC"""
    ).fetchall()
    conn.close()
    return render_template("movements.html", movements=rows, moves=moves)
@app.route("/correction", methods=["GET", "POST"])
def correction():
    denied = require_role("director", "warehouse")
    if denied:
        return denied
    conn = get_db()
    error = None
    if request.method == "POST":
        component_id = int(request.form["component_id"])
        change = int(request.form["change"])
        try:
            correct_stock(conn, component_id, change)
            conn.close()
            return redirect(url_for("components"))
        except ValueError as e:
            error = str(e)
    rows = conn.execute("SELECT id, part_number, name, quantity FROM components ORDER BY part_number").fetchall()
    conn.close()
    return render_template("correction.html", components=rows, error=error)
@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    denied = require_role()
    if denied:
        return denied
    error = None
    message = None
    if request.method == "POST":
        old = request.form["old_password"]
        new = request.form["new_password"]
        new2 = request.form["new_password2"]
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (session["username"],)
        ).fetchone()
        if not check_password_hash(user["password_hash"], old):
            error = "Старата парола е грешна"
        elif new != new2:
            error = "Новите пароли не съвпадат"
        elif len(new) < 6:
            error = "Новата парола трябва да е поне 6 символа"
        else:
            with conn:
                conn.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (generate_password_hash(new), user["id"])
                )
            message = "Паролата е сменена"
        conn.close()
    return render_template("change_password.html", error=error, message=message)
@app.route("/products")
def products():
    denied = require_role()
    if denied:
        return denied
    conn = get_db()
    rows = conn.execute("SELECT * FROM products ORDER BY code").fetchall()
    conn.close()
    return render_template("products.html", products=rows)
    moves = conn.execute(
        """SELECT m.created_at, p.code, m.change, m.reason, m.order_id
           FROM product_movements m
           JOIN ___ p ON p.id = m.___
           ORDER BY m.id DESC"""
    ).fetchall()
@app.route("/products/<int:product_id>", methods=["GET", "POST"])
def product_detail(product_id):
    denied = require_role()
    if denied:
        return denied
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()  
    if product is None:
        conn.close()
        return "Няма такъв продукт", 404
    if request.method == "POST":
        if session["role"] != "director":
            conn.close()
            return "Нямате достъп", 403
        component_id = int(request.form["component_id"])
        quantity = int(request.form["quantity"])
        set_bom_item(conn, product_id, component_id, quantity)
        conn.close()
        return redirect(url_for("product_detail", product_id=product_id))
    bom = conn.execute("""
        SELECT c.part_number, c.name, b.quantity
        FROM bom_items b
        JOIN components c ON b.component_id = c.id
        WHERE b.product_id = ?
        ORDER BY c.part_number
    """, (product_id,)).fetchall()
    processes = conn.execute("""
        SELECT pp.process_id, pr.name, pp.hours
        FROM product_processes pp
        JOIN processes pr ON pp.process_id = pr.id
        WHERE pp.product_id = ?
    """, (product_id,)).fetchall()
    cost = None
    all_components = []
    if session["role"] == "director":
        cost = calc_cost(conn, product_id)
        all_components = conn.execute("SELECT id, part_number, name FROM components ORDER BY part_number").fetchall()
    conn.close()
    return render_template("product_detail.html", product=product, bom=bom, processes=processes, cost=cost, all_components=all_components)


@app.route("/orders", methods=["GET", "POST"])
def orders():
    denied = require_role()
    if denied:
        return denied
    conn = get_db()
    if request.method == "POST":
        if session["role"] != "director":
            conn.close()
            return "Нямате достъп", 403
        product_id = int(request.form["product_id"])
        quantity = int(request.form["quantity"])
        due_date = request.form["due_date"] or None
        with conn:
            conn.execute(
                "INSERT INTO orders (product_id, quantity, due_date) VALUES (?, ?, ?)",
                (product_id, quantity, due_date)
            )
        conn.close()
        return redirect(url_for("orders"))
    rows = conn.execute("""
        SELECT o.id, p.code, o.quantity, o.due_date, o.status
        FROM orders o
        JOIN products p ON o.product_id = p.id
        ORDER BY o.id DESC
    """).fetchall()
    products = conn.execute("SELECT id, code, name FROM products ORDER BY code").fetchall()
    conn.close()
    return render_template("orders.html", orders=rows, products=products)

@app.route("/orders/<int:order_id>/start", methods=["POST"])
def order_start(order_id):
    denied = require_role("director", "production")        
    if denied:
        return denied
    conn = get_db()
    try:
        start_production(conn, order_id)
    except ValueError as e:
        flash(str(e))
    except ValueError as e:
        flash(str(e))
    conn.close()
    return redirect(url_for("orders"))
@app.route("/orders/<int:order_id>/finish", methods=["POST"])
def order_finish(order_id):
    denied = require_role("director", "production")
    if denied:
        return denied
    conn = get_db()
    try:
        finish_order(conn, order_id)
    except ValueError as e:
        flash(str(e))
    conn.close()
    return redirect(url_for("orders"))


@app.route("/orders/<int:order_id>/cancel", methods=["POST"])
def order_cancel(order_id):
    denied = require_role("director")
    if denied:
        return denied
    conn = get_db()
    try:
        cancel_order(conn, order_id)
    except ValueError as e:
        flash(str(e))
    conn.close()
    return redirect(url_for("orders"))
@app.route("/report")
def report():
    denied = require_role("director")
    if denied:
        return denied
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY code").fetchall()
    rows = []
    for p in products:
        cost = calc_cost(conn, p["id"])
        profit = p["sale_price"] - cost["total"]
        percent = profit / p["sale_price"] * 100
        rows.append({"code": p["code"], "name": p["name"], "cost": cost["total"],
                     "price": p["sale_price"], "profit": profit, "percent": percent})
    conn.close()
    return render_template("report.html", rows=rows)
@app.route("/forecast")
def forecast():
    denied = require_role("director", "warehouse")
    if denied:
        return denied
    conn = get_db()
    components = conn.execute("SELECT * FROM components ORDER BY part_number").fetchall()
    rows = []
    for c in components:
        f = forecast_component(conn, c["id"])
        if f is None:
            continue
        rows.append({"part_number": c["part_number"], "name": c["name"], "quantity": c["quantity"],
                     "per_day": f["per_day"], "days_left": f["days_left"], "order_qty": f["order_qty"]})
    conn.close()
    rows.sort(key=lambda r: r["days_left"])
    return render_template("forecast.html", rows=rows)
@app.route("/products/<int:product_id>/price", methods=["POST"])
def product_price(product_id):
    denied = require_role("director")
    if denied:
        return denied
    try:
        price = float(request.form["sale_price"])
        if price <= 0:
            raise ValueError("Цената трябва да е по-голяма от 0")
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("product_detail", product_id=product_id))
    conn = get_db()
    with conn:
        conn.execute("UPDATE products SET sale_price = ? WHERE id = ?", (price, product_id))
    conn.close()
    return redirect(url_for("product_detail", product_id=product_id))
@app.route("/products/<int:product_id>/hours", methods=["POST"])
def product_hours(product_id):
    denied = require_role("director")
    if denied:
        return denied
    try:
        process_id = int(request.form["process_id"])
        hours = float(request.form["hours"])
        if hours <= 0:
            raise ValueError("Часовете трябва да са повече от 0")
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("product_detail", product_id=product_id))
    conn = get_db()
    with conn:
        conn.execute(
            "UPDATE product_processes SET hours = ? WHERE product_id = ? AND process_id = ?",
            (hours, product_id, process_id),
        )
    conn.close()
    return redirect(url_for("product_detail", product_id=product_id))
@app.route("/sales", methods=["GET", "POST"])
def sales():
    denied = require_role("director", "warehouse")
    if denied:
        return denied
    conn = get_db()
    if request.method == "POST":
        if session["role"] != "director":
            conn.close()
            return "Нямате достъп", 403
        customer = request.form["customer"]
        product_id = int(request.form["product_id"])
        quantity = int(request.form["quantity"])
        with conn:
            conn.execute(
                "INSERT INTO sales (customer, product_id, quantity) VALUES (?, ?, ?)",
                (customer, product_id, quantity),
            )
        conn.close()
        return redirect(url_for("sales"))
    rows = conn.execute("""
        SELECT s.id, s.customer, p.code, s.quantity, p.quantity AS in_stock, s.status
        FROM sales s
        JOIN products p ON s.product_id = p.id
        ORDER BY s.id DESC
    """).fetchall()
    products = conn.execute("SELECT id, code, name, quantity FROM products ORDER BY code").fetchall()
    conn.close()
    return render_template("sales.html", sales=rows, products=products,)
@app.route("/sales/<int:sale_id>/ship", methods=["POST"])
def sale_ship(sale_id):
    denied = require_role("director", "warehouse")
    if denied:
        return denied
    conn = get_db()
    try:
        ship_sale(conn, sale_id)
    except ValueError as e:
        flash(str(e))
    conn.close()
    return redirect(url_for("sales"))


@app.route("/sales/<int:sale_id>/cancel", methods=["POST"])
def sale_cancel(sale_id):
    denied = require_role("director")
    if denied:
        return denied
    conn = get_db()
    try:
        cancel_sale(conn, sale_id)
    except ValueError as e:
        flash(str(e))
    conn.close()
    return redirect(url_for("sales"))
if __name__ == "__main__":
    app.run(debug=True)