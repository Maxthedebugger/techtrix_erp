CREATE TABLE 

users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('director', 'warehouse', 'production'))
);

components (
    id INTEGER PRIMARY KEY,
    part_number TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    type TEXT,
    value TEXT,
    quantity INTEGER DEFAULT 0 CHECK (quantity >= 0),
    min_quantity INTEGER CHECK (min_quantity >= 0),
    price REAL CHECK (price >= 0),
    supplier TEXT
);