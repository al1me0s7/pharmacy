from app.models.database import Database
from werkzeug.security import generate_password_hash, check_password_hash

class Admin:
    @staticmethod
    def create(login, password):
        # CRUD створення адміністратора
        hashed = generate_password_hash(password)
        return Database.execute(
            'INSERT INTO admins (login, password_hash) VALUES (%s,%s) RETURNING admin_id',
            (login, hashed),
            returning=True
        )

    @staticmethod
    def find_by_login(login):
        # CRUD: Знайти - пошук адміністратора за логіном
        return Database.fetchone('SELECT * FROM admins WHERE login = %s', (login,))

    @staticmethod
    def find_by_id(admin_id):
        # CRUD: Знайти - пошук адміністратора за ID
        return Database.fetchone('SELECT * FROM admins WHERE admin_id = %s', (admin_id,))

    @staticmethod
    def verify_password(admin, password):
        return check_password_hash(admin['password_hash'], password)