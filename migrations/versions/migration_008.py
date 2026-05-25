# тут ми додаємо підтримку множественних ліків в бронюваннях і рахунків
def upgrade():
    return '''
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS items_json TEXT;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS total_sum DECIMAL(10, 2) DEFAULT 0;

CREATE TABLE IF NOT EXISTS booking_items (
    booking_id INTEGER REFERENCES bookings(booking_id) ON DELETE CASCADE,
    medicine_id INTEGER REFERENCES medicines(medicine_id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    price_at_booking DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (booking_id, medicine_id)
);

CREATE TABLE IF NOT EXISTS admin_reports (
    report_id SERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,
    generated_by INTEGER REFERENCES admins(admin_id) ON DELETE SET NULL,
    date_from DATE,
    date_to DATE,
    report_data TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

def downgrade():
    return '''
ALTER TABLE bookings DROP COLUMN IF EXISTS items_json;
ALTER TABLE bookings DROP COLUMN IF EXISTS total_sum;
DROP TABLE IF EXISTS booking_items;
DROP TABLE IF EXISTS admin_reports;
'''
