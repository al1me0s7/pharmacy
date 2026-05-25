# додаємо inventory_id як PK, видаляємо pharmacy_prices

def upgrade():
    return '''
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS inventory_id SERIAL PRIMARY KEY;
DROP TABLE IF EXISTS pharmacy_prices;
'''

def downgrade():
    return '''
ALTER TABLE inventory DROP COLUMN IF EXISTS inventory_id;
CREATE TABLE IF NOT EXISTS pharmacy_prices (
    medicine_id INTEGER REFERENCES medicines(medicine_id) ON DELETE CASCADE,
    pharmacy_id INTEGER REFERENCES pharmacies(pharmacy_id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (medicine_id, pharmacy_id)
);
'''
