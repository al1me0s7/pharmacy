# тут ми додаємо таблицю pharmacy_prices для зберігання цін на ліки в різних аптеках
def upgrade():
    return '''
    CREATE TABLE IF NOT EXISTS pharmacy_prices (
        medicine_id INTEGER REFERENCES medicines(medicine_id) ON DELETE CASCADE,
        pharmacy_id INTEGER REFERENCES pharmacies(pharmacy_id) ON DELETE CASCADE,
        price DECIMAL(10, 2) NOT NULL,
        PRIMARY KEY (medicine_id, pharmacy_id)
    )
    '''

def downgrade():
    return '''DROP TABLE IF EXISTS pharmacy_prices'''