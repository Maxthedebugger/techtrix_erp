CREATE TABLE components (
    id INTEGER PRIMARY KEY,
    part_number TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    type TEXT,
    value TEXT,
    quantity INTEGER DEFAULT 0,
    min_quantity INTEGER,
    price REAL,
    supplier TEXT,
);