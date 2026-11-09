from database import get_db, init_db 

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
    conn.commit()          
    conn.close()           
    
if __name__ == "__main__":
    seed()