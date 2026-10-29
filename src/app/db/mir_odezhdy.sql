DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS stock_items CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS variants CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    login VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100), 
    role VARCHAR(50) NOT NULL
);

CREATE TABLE variants (
    variant_id SERIAL PRIMARY KEY,
    variant_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    image_url VARCHAR(255),
    product_name VARCHAR(150) NOT NULL,
    production VARCHAR(150) NOT NULL,
    description TEXT,
    composition TEXT,
    base_price NUMERIC(10, 2) NOT NULL CHECK (base_price >= 0),
    CONSTRAINT uq_product_model UNIQUE (product_name, production)
);

CREATE TABLE stock_items (
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
    variant_id INT REFERENCES variants(variant_id) ON DELETE CASCADE,
    stock_quantity INT NOT NULL CHECK (stock_quantity >= 0),
    variant_price NUMERIC(10, 2) NOT NULL CHECK (variant_price >= 0),
    PRIMARY KEY (product_id, variant_id)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_number INT NOT NULL,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    user_id INT REFERENCES users(user_id) ON DELETE SET NULL,
    customer_fio VARCHAR(250),
    category VARCHAR(100),
    product_id INT REFERENCES products(product_id) ON DELETE SET NULL,
    product_name_raw VARCHAR(150),
    production VARCHAR(150),
    variant_id INT REFERENCES variants(variant_id) ON DELETE SET NULL,
    variant_name_raw VARCHAR(100),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_name ON products(product_name);
CREATE INDEX idx_orders_number ON orders(order_number);
CREATE INDEX idx_orders_date ON orders(order_date);