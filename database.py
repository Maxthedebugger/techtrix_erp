import sqlite3 
def get_db():                          # вградената библиотека за SQLite
    conn = sqlite3.connect("techtrix.db")           # отваря файла (ако го няма, го създава) и връща връзка
    conn.row_factory = sqlite3.Row           # редовете стават като речник
    conn.execute("PRAGMA foreign_keys = ON") # включва проверката на REFERENCES
    return conn