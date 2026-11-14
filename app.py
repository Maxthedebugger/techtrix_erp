from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash
from database import get_db
from services.inventory import receive_delivery

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
if __name__ == "__main__":
    app.run(debug=True)