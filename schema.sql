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
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    sale_price REAL CHECK(sale_price >= 0)
);
CREATE TABLE bom_items (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    component_id INTEGER NOT NULL REFERENCES components(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    UNIQUE (product_id, component_id)
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer TEXT NOT NULL,
    product_id INTEGER REFERENCES products(id) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity  > 0),
    due_date TEXT,
    status TEXT NOT NULL DEFAULT 'new' CHECK(status IN('new','in_production','done', 'shipped','cancelled')),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE stock_movements (
    id INTEGER PRIMARY KEY,
    component_id INTEGER REFERENCES components(id) NOT NULL, 
    change INTEGER NOT NULL,
    reason TEXT NOT NULL CHECK(reason IN ('delivery', 'production', 'correction')),
    order_id INTEGER REFERENCES orders(id),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value REAL NOT NULL
    
);