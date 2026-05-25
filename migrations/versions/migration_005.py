# тут ми додаємо таблицю admins для зберігання інформації про адміністраторів системи
def upgrade():
    return '''
CREATE TABLE IF NOT EXISTS admins (
    admin_id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
'''

def downgrade():
    return '''DROP TABLE IF EXISTS admins'''