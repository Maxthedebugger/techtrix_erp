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
def import_bom(conn, product_id, text):
    items = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if line == "" or line.startswith("#"):
            continue
        if ";" in line:
            parts = line.split(";")
        elif "\t" in line:
            parts = line.split("\t")
        else:
            parts = line.split(",")
        parts = [p.strip() for p in parts]
        if len(parts) < 2 or parts[0] == "":
            raise ValueError(f"Ред {line_no}: трябва да е КОД;БРОЙ")
        part_number = parts[0].upper()
        try:
            quantity = int(parts[1])
        except ValueError:
            raise ValueError(f"Ред {line_no}: „{parts[1]}“ не е цяло число")
        if quantity <= 0:
            raise ValueError(f"Ред {line_no}: бройката трябва да е повече от 0")
        name = parts[2] if len(parts) > 2 and parts[2] != "" else part_number
        items.append((part_number, quantity, name))
    if not items:
        raise ValueError("Файлът е празен")

    created = []
    with conn:
        conn.execute("DELETE FROM bom_items WHERE product_id = ?", (product_id,))
        for part_number, quantity, name in items:
            comp = conn.execute("SELECT id, active FROM components WHERE UPPER(part_number) = ?", (part_number,)).fetchone()
            if comp is None:
                cur = conn.execute(
                    "INSERT INTO components (part_number, name, quantity, min_quantity, price) VALUES (?, ?, 0, 0, 0)",
                    (part_number, name),
                )
                component_id = cur.lastrowid
                created.append(part_number)
            else:
                component_id = comp["id"]
                if comp["active"] == 0:
                    conn.execute("UPDATE components SET active = 1 WHERE id = ?", (component_id,))
            conn.execute(
                """INSERT INTO bom_items (product_id, component_id, quantity) VALUES (?, ?, ?)
                   ON CONFLICT (product_id, component_id) DO UPDATE SET quantity = quantity + excluded.quantity""",
                (product_id, component_id, quantity),
            )
    return len(items), created
