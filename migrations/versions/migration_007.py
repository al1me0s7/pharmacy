# migration_medicines.py
def upgrade():
    return '''
ALTER TABLE medicines
    DROP CONSTRAINT IF EXISTS medicines_manufacturer_id_fkey,
    DROP CONSTRAINT IF EXISTS medicines_category_id_fkey;

ALTER TABLE medicines
    ADD CONSTRAINT medicines_manufacturer_id_fkey
        FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id) ON DELETE CASCADE,
    ADD CONSTRAINT medicines_category_id_fkey
        FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL;
'''

def downgrade():
    return '''
ALTER TABLE medicines
    DROP CONSTRAINT IF EXISTS medicines_manufacturer_id_fkey,
    DROP CONSTRAINT IF EXISTS medicines_category_id_fkey;

ALTER TABLE medicines
    ADD CONSTRAINT medicines_manufacturer_id_fkey
        FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id),
    ADD CONSTRAINT medicines_category_id_fkey
        FOREIGN KEY (category_id) REFERENCES categories(category_id);
'''
