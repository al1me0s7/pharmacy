# тут ми додаємо стовпці status_last_updated до таблиць orders та bookings
def upgrade():
    return '''
ALTER TABLE orders ADD COLUMN IF NOT EXISTS status_last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS status_last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
'''

def downgrade():
    return '''
ALTER TABLE orders DROP COLUMN IF EXISTS status_last_updated;
ALTER TABLE bookings DROP COLUMN IF EXISTS status_last_updated;
'''