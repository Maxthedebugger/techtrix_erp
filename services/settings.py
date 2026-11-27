DEFAULT_COMPANY_NAME = "Techtrix ERP"


def get_company_name(conn):
    """Връща името на фирмата от настройките (или стандартното, ако още не е сменяно)."""
    row = conn.execute("SELECT value FROM settings WHERE key = 'company_name'").fetchone()
    if row is None:
        return DEFAULT_COMPANY_NAME
    return row["value"]


def set_company_name(conn, name):
    """Записва новото име на фирмата. Връща записаното име."""
    name = name.strip()
    if name == "":
        raise ValueError("Името на фирмата не може да е празно")
    if len(name) > 40:
        raise ValueError("Името на фирмата може да е най-много 40 знака")
    if not any(ch.isalpha() for ch in name):
        raise ValueError("Името на фирмата трябва да съдържа поне една буква")
    with conn:
        conn.execute(
            """INSERT INTO settings (key, value) VALUES ('company_name', ?)
               ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
            (name,),
        )
    return name