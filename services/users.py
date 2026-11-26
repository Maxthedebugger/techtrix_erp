from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

ROLES = {"director": "Директор", "warehouse": "Началник склад", "production": "Производство"}


def check_new_password(password, password2):
    if password != password2:
        raise ValueError("Паролите не съвпадат")
    if len(password) < 6:
        raise ValueError("Паролата трябва да е поне 6 символа")


def create_user(conn, username, role, password, password2):
    username = username.strip()
    if username == "":
        raise ValueError("Въведи потребителско име")
    if role not in ROLES:
        raise ValueError("Няма такава роля")
    check_new_password(password, password2)
    exists = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if exists:
        raise ValueError(f"Потребител „{username}“ вече съществува")
    with conn:
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), role),
        )


def set_password(conn, user_id, password, password2):
    check_new_password(password, password2)
    user = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    if user is None:
        raise ValueError("Няма такъв потребител")
    with conn:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(password), user_id),
        )
    return user["username"]


def set_role(conn, user_id, role):
    if role not in ROLES:
        raise ValueError("Няма такава роля")
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user is None:
        raise ValueError("Няма такъв потребител")
    if user["role"] == "director" and role != "director":
        directors = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'director'").fetchone()[0]
        if directors <= 1:
            raise ValueError("Това е последният директор. Първо направи друг потребител директор.")
    with conn:
        conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    return user["username"]


def _last_sunday(year, month):
    # последната неделя на месеца (тогава се мести часът)
    day = datetime(year, month + 1, 1) - timedelta(days=1)
    while day.weekday() != 6:
        day = day - timedelta(days=1)
    return day


def bg_time(text):
    """Превръща време от базата (UTC) в българско време: 26.11.2026 22:56"""
    if not text:
        return ""
    t = datetime.strptime(text[:19], "%Y-%m-%d %H:%M:%S")
    summer_start = _last_sunday(t.year, 3) + timedelta(hours=1)
    summer_end = _last_sunday(t.year, 10) + timedelta(hours=1)
    offset = 3 if summer_start <= t < summer_end else 2
    return (t + timedelta(hours=offset)).strftime("%d.%m.%Y %H:%M")