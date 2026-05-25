#  міграції для створення початкової схеми бази даних
def upgrade():
    return '''
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    postal_code VARCHAR(20),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_visible BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS manufacturers (
    manufacturer_id SERIAL PRIMARY KEY,
    manufacturer_name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    city VARCHAR(50),
    address TEXT,
    contact_email VARCHAR(100),
    contact_phone VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS medicines (
    medicine_id SERIAL PRIMARY KEY,
    manufacturer_id INTEGER REFERENCES manufacturers(manufacturer_id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(category_id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    active_substance VARCHAR(100),
    dosage_form VARCHAR(50),
    dosage_value VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    quantity_in_stock INTEGER DEFAULT 0,
    expiration_date DATE,
    prescription_required BOOLEAN DEFAULT FALSE,
    contraindications TEXT,
    composition TEXT,
    usage_instructions TEXT,
    storage_conditions TEXT,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cities (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(50) NOT NULL UNIQUE,
    region VARCHAR(50),
    postal_code_prefix VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS pharmacies (
    pharmacy_id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(city_id) ON DELETE SET NULL,
    pharmacy_name VARCHAR(100) NOT NULL,
    address VARCHAR(200) NOT NULL,
    working_hours VARCHAR(100),
    contact_phone VARCHAR(20),
    email VARCHAR(100),
    has_delivery BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3, 2),
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_address TEXT,
    delivery_method VARCHAR(50),
    delivery_status VARCHAR(50) DEFAULT 'pending',
    total_sum DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'cash_on_delivery',
    comment TEXT
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    medicine_id INTEGER REFERENCES medicines(medicine_id) ON DELETE CASCADE,
    pharmacy_id INTEGER REFERENCES pharmacies(pharmacy_id) ON DELETE CASCADE,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pickup_deadline TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS order_medicine (
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    medicine_id INTEGER REFERENCES medicines(medicine_id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    price_at_purchase DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2),
    PRIMARY KEY (order_id, medicine_id)
);

CREATE TABLE IF NOT EXISTS inventory (
    medicine_id INTEGER REFERENCES medicines(medicine_id) ON DELETE CASCADE,
    pharmacy_id INTEGER REFERENCES pharmacies(pharmacy_id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0,
    selling_price DECIMAL(10, 2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (medicine_id, pharmacy_id)
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    medicine_id INTEGER REFERENCES medicines(medicine_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''
# Видалення всіх таблиць при відкаті міграції
def downgrade():
    return '''DROP TABLE IF EXISTS reviews, inventory, order_medicine, bookings, orders, pharmacies, cities, medicines, manufacturers, categories, users'''