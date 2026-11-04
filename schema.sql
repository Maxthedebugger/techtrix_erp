CREATE TABLE 

users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('director', 'warehouse', 'production'))
);
CREATE TABLE
components (
    id INTEGER PRIMARY KEY,
    part_number TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    type TEXT,
    value TEXT,
    quantity INTEGER  NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    min_quantity INTEGER CHECK (min_quantity >= 0),
    price REAL CHECK (price >= 0),
    supplier TEXT
);
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    labor_hours REAL NOT NULL CHECK(labor_hours >= 0),
    sale_price REAL CHECK(sale_price >= 0)
);
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    component_id INTEGER NOT NULL REFERENCES components(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0)
);