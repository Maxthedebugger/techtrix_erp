import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from seed import seed
from services.costing import calc_cost
from services.inventory import correct_stock
from services.production import start_production, finish_order
from services.forecast import forecast_component
from services.sales import ship_sale


@pytest.fixture
def conn(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    seed()
    c = database.get_db()
    yield c
    c.close()


def new_order(conn, product_id, quantity):
    with conn:
        cur = conn.execute(
            "INSERT INTO orders (product_id, quantity) VALUES (?, ?)",
            (product_id, quantity),
        )
    return cur.lastrowid


def test_cost_of_hum1(conn):
    cost = calc_cost(conn, 1)
    assert round(cost["total"], 2) == 18.98


def test_correction_cannot_go_negative(conn):
    with pytest.raises(ValueError):
        correct_stock(conn, 4, -100000)


def test_not_enough_components(conn):
    order_id = new_order(conn, 3, 100)
    with pytest.raises(ValueError, match="Не достигат"):
        start_production(conn, order_id)


def test_full_order_flow(conn):
    order_id = new_order(conn, 1, 5)
    start_production(conn, order_id)
    finish_order(conn, order_id)
    stock = conn.execute("SELECT quantity FROM products WHERE id = 1").fetchone()["quantity"]
    with conn:
        sale_id = conn.execute(
            "INSERT INTO sales (customer, product_id, quantity) VALUES ('Тест', 1, 5)"
        ).lastrowid
    ship_sale(conn, sale_id)
    stock = conn.execute("SELECT quantity FROM products WHERE id = 1").fetchone()["quantity"]
    assert stock == 0
    

def test_forecast_finds_daily_usage(conn):
    with conn:
        for days_ago in range(10, 0, -1):
            conn.execute(
                "INSERT INTO stock_movements (component_id, change, reason, created_at) "
                "VALUES (4, -5, 'production', datetime('now', ?))",
                (f"-{days_ago} days",),
            )
    f = forecast_component(conn, 4)
    assert round(f["per_day"]) == 5
    f = forecast_component(conn, 4)
    assert round(f["per_day"]) == 5

def test_delivery_many(conn):
    from services.inventory import receive_delivery_many
    before = conn.execute("SELECT quantity FROM components WHERE part_number = 'C-100N'").fetchone()[0]
    n = receive_delivery_many(conn, [("c-100n", 100, 0.03), ("PCB-ETH1", 5, 3.0)])
    assert n == 2
    after = conn.execute("SELECT quantity FROM components WHERE part_number = 'C-100N'").fetchone()[0]
    assert after == before + 100
    # грешен код: нищо не се записва
    with pytest.raises(ValueError):
        receive_delivery_many(conn, [("C-100N", 1, 0.03), ("NOPE", 1, 1.0)])
    again = conn.execute("SELECT quantity FROM components WHERE part_number = 'C-100N'").fetchone()[0]
    assert again == after