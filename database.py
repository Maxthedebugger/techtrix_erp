import sqlite3 


def get_db():                          
    conn = sqlite3.connect("techtrix.db")           
    conn.row_factory = sqlite3.Row          
    conn.execute("PRAGMA foreign_keys = ON") 
    return conn


def init_db():
    conn = get_db()
    with open("schema.sql", encoding="utf-8") as f:  # отваря файла и го затваря сам след блока
        sql = f.read()                                # целият текст отива в променливата sql
        conn.executescript(sql)   # изпълнява МНОГО SQL команди наведнъж (execute може само една)
        conn.commit()             # „запиши промените“
        conn.close()              # затвори връзката
if __name__ == "__main__":
    init_db()