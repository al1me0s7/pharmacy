def upgrade():
    return '''
ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS city_name VARCHAR(100);
'''

def downgrade():
    return '''
ALTER TABLE orders
    DROP COLUMN IF EXISTS city_name;
'''
