from flask import Flask, render_template, request
from werkzeug.security import check_password_hash
from database import get_db

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", name="Макси")


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
            return "Успешен вход! Роля: " + user["role"]
        return "Грешно име или парола"
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)