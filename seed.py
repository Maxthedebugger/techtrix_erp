from database import get_db, init_db 
from werkzeug.security import generate_password_hash

def seed():
    init_db()              
    conn = get_db()       
    conn.execute(
        "INSERT INTO processes (name, hourly_rate) VALUES (?, ?)",
        ("SMT монтаж", 15.00)
    )
    conn.execute(
        "INSERT INTO processes (name, hourly_rate) VALUES (?, ?)",
        ("Ръчно запояване", 12.00)
    )
    conn.execute(
        "INSERT INTO processes (name, hourly_rate) VALUES (?, ?)",
        ("Тест", 10.00)
    )
    conn.execute(          
        "INSERT INTO settings (key, value) VALUES (?, ?)",
        ("overhead_percent", 15)
    )

    components = [
        ("PCB-HUM1", "Печатна платка PCB-HUM1", "платка", 1.50, 20),
        ("PCB-ETH1", "Печатна платка PCB-ETH1", "платка", 3.00, 20),
        ("PCB-GSM1", "Печатна платка PCB-GSM1", "платка", 3.50, 20),
        ("STM32F103", "Микроконтролер STM32F103", "чип", 3.50, 50),
        ("SHT31", "Датчик за влажност SHT31", "датчик", 3.00, 20),
        ("W5500", "Ethernet чип W5500", "чип", 2.50, 20),
        ("SIM7080G", "LTE модем SIM7080G", "чип", 9.00, 10),
        ("AMS1117-3.3", "Регулатор AMS1117-3.3", "чип", 0.20, 50),
        ("R-10K", "Резистор 10 kΩ", "резистор", 0.02, 500),
        ("C-100N", "Кондензатор 100 nF", "кондензатор", 0.03, 500),
        ("TB-2P", "Клемник 2 пина", "конектор", 0.40, 100),
        ("RJ45-MAG", "Конектор RJ45 с трансформатор", "конектор", 1.50, 20),
        ("SIM-HOLDER", "Държач за SIM карта", "конектор", 0.40, 20),
        ("ANT-LTE", "LTE антена", "антена", 2.00, 10),
        ("BOX-60x40", "Пластмасова кутия 60×40×20 mm", "кутия", 1.50, 20),
        ("BOX-DIN", "Кутия за DIN шина", "кутия", 4.00, 30),
    ]
    for component in components:
        conn.execute(
            "INSERT INTO components (part_number, name, type, price, min_quantity) VALUES (?, ?, ?, ?, ?)",
            component
        )

    products = [
            ("TX-HUM1", "Сензор за влажност", 29.00),
            ("TX-ETH1", "Ethernet контролер", 59.00),
            ("TX-GSM1", "LTE контролер", 89.00),
    ]
    for product in products:
        conn.execute(
            "INSERT INTO products (code, name, sale_price) VALUES (?, ?, ?)",
            product
        )

        bom = [
        ("TX-HUM1", "PCB-HUM1", 1),
        ("TX-HUM1", "SHT31", 1),
        ("TX-HUM1", "STM32F103", 1),
        ("TX-HUM1", "AMS1117-3.3", 1),
        ("TX-HUM1", "R-10K", 4),
        ("TX-HUM1", "C-100N", 4),
        ("TX-HUM1", "TB-2P", 1),
        ("TX-HUM1", "BOX-60x40", 1),
        ("TX-ETH1", "PCB-ETH1", 1),
        ("TX-ETH1", "STM32F103", 1),
        ("TX-ETH1", "W5500", 1),
        ("TX-ETH1", "RJ45-MAG", 1),
        ("TX-ETH1", "AMS1117-3.3", 1),
        ("TX-ETH1", "R-10K", 8),
        ("TX-ETH1", "C-100N", 10),
        ("TX-ETH1", "TB-2P", 3),
        ("TX-ETH1", "BOX-DIN", 1),
        ("TX-GSM1", "PCB-GSM1", 1),
        ("TX-GSM1", "STM32F103", 1),
        ("TX-GSM1", "SIM7080G", 1),
        ("TX-GSM1", "SIM-HOLDER", 1),
        ("TX-GSM1", "ANT-LTE", 1),
        ("TX-GSM1", "AMS1117-3.3", 1),
        ("TX-GSM1", "R-10K", 8),
        ("TX-GSM1", "C-100N", 10),
        ("TX-GSM1", "TB-2P", 3),
        ("TX-GSM1", "BOX-DIN", 1),
    ]
    for item in bom:
        conn.execute(
            """INSERT INTO bom_items (product_id, component_id, quantity)
               VALUES ((SELECT id FROM products WHERE code = ?),
                       (SELECT id FROM components WHERE part_number = ?),
                       ?)""",
            item
        )

    product_processes = [
        ("TX-HUM1", "SMT монтаж", 0.2),
        ("TX-HUM1", "Ръчно запояване", 0.1),
        ("TX-HUM1", "Тест", 0.2),
        ("TX-ETH1", "SMT монтаж", 0.3),
        ("TX-ETH1", "Ръчно запояване", 0.25),
        ("TX-ETH1", "Тест", 0.25),
        ("TX-GSM1", "SMT монтаж", 0.4),
        ("TX-GSM1", "Ръчно запояване", 0.3),
        ("TX-GSM1", "Тест", 0.3),
    ]
    for product_process in product_processes:
        conn.execute(
             """INSERT INTO product_processes (product_id, process_id, hours)
                VALUES ((SELECT id FROM products WHERE code = ?),
                        (SELECT id FROM processes WHERE name = ?),
                        ?)""",
            product_process
        )
    deliveries = [
        ("PCB-HUM1", 100, 1.50),
        ("PCB-ETH1", 50, 3.00),
        ("PCB-GSM1", 15, 3.50),
        ("STM32F103", 200, 3.50),
        ("SHT31", 100, 3.00),
        ("W5500", 50, 2.50),
        ("SIM7080G", 30, 9.00),
        ("AMS1117-3.3", 200, 0.20),
        ("R-10K", 2000, 0.02),
        ("C-100N", 2000, 0.03),
        ("TB-2P", 300, 0.40),
        ("RJ45-MAG", 50, 1.50),
        ("SIM-HOLDER", 30, 0.40),
        ("ANT-LTE", 8, 2.00),
        ("BOX-60x40", 100, 1.50),
        ("BOX-DIN", 80, 4.00),
    ]
    for part, qty, price in deliveries:
        conn.execute(
            "UPDATE components SET quantity = quantity + ? WHERE part_number = ?",
            (qty, part)
        )
        conn.execute(
            "INSERT INTO stock_movements (component_id, change, unit_price, reason) VALUES ((SELECT id FROM components WHERE part_number = ?), ?, ?, 'delivery')",
            (part, qty, price)
        )
        users = [
        ("director", "director123", "director"),
        ("warehouse", "warehouse123", "warehouse"),
        ("production", "production123", "production"),
    ]
        
    for username, password, role in users:
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), role)
        )
            
        
        
     
    conn.commit()          
    conn.close()     

    
    
    
if __name__ == "__main__":
    seed()