# тут ми додаємо таблицю reviews для зберігання відгуків користувачів про ліки
def upgrade():
    return '''
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    medicine_id INTEGER REFERENCES medicines(medicine_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

def downgrade():
    return '''DROP TABLE IF EXISTS reviews'''