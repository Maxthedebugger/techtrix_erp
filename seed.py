import sqlite3 
import os 
from database import get_db, init_db 

def get_db():                          
    conn = sqlite3.connect("techtrix.db")           
    conn.row_factory = sqlite3.Row          
    conn.execute("PRAGMA foreign_keys = ON") 
    return conn


def init_db():
                          
    if os.path.exists("techtrix.db"):    
        os.remove("techtrix.db")        
    conn = get_db()
    with open("schema.sql", encoding="utf-8") as f:  
        sql = f.read()                                
    conn.executescript(sql)  
    conn.commit()            
    conn.close()         

def seed():
    init_db()              
    conn = get_db()       
    conn.execute(
        "INSERT INTO processes (name, hourly_rate) VALUES (?, ?)",
        ("SMT монтаж", 15.00)
    )
    conn.execute(          
        "INSERT INTO settings (key, value) VALUES (?, ?)",
        ("overhead_percent", 15)
    )

    

    conn.commit()          
    conn.close()           
    
if __name__ == "__main__":
    seed()