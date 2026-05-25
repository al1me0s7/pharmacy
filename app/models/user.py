from app.models.database import Database
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    @staticmethod
    def create(full_name, email, password, phone, address=None, city=None, postal_code=None):
        # CRUD: Створити користувача (INSERT)
        hashed = generate_password_hash(password)
        return Database.execute(
            'INSERT INTO users (full_name, email, password_hash, phone_number, address, city, postal_code) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING user_id',
            (full_name, email, hashed, phone, address, city, postal_code),
            returning=True
        )

    @staticmethod
    def find_by_email(email):
        # CRUD: Знайти користувача за email (SELECT WHERE)
        return Database.fetchone('SELECT * FROM users WHERE email = %s', (email,))

    @staticmethod
    def find_by_id(user_id):
        # CRUD: Знайти користувача за ID (SELECT WHERE)
        return Database.fetchone('SELECT * FROM users WHERE user_id = %s', (user_id,))

    @staticmethod
    def verify_password(user, password):
        return check_password_hash(user['password_hash'], password)

    @staticmethod
    def update(user_id, full_name, last_name, phone, address, city, postal_code):
        # CRUD: Оновити профіль (UPDATE)
        Database.execute(
            'UPDATE users SET full_name=%s, last_name=%s, phone_number=%s, address=%s, city=%s, postal_code=%s WHERE user_id=%s',
            (full_name, last_name, phone, address, city, postal_code, user_id)
        )

    @staticmethod
    def delete(user_id):
        # CRUD: Видалити користувача (DELETE CASCADE)
        Database.execute('DELETE FROM users WHERE user_id = %s', (user_id,))