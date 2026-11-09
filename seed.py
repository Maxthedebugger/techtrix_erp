import sqlite3 
import os 
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

    

    conn.commit()          
    conn.close()           
    
if __name__ == "__main__":
    seed()