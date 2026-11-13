from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash
from database import get_db

app = Flask(__name__)

app.secret_key = "techtrix-dev-key-2026"

@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", name=session["username"], role=session["role"])

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
if __name__ == "__main__":
    app.run(debug=True)