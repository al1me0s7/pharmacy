from app.models.database import Database

class Category:
    @staticmethod
    def get_all():
        # CRUD: Отримати всі категорії (SELECT ORDER BY)
        return Database.fetchall('SELECT * FROM categories ORDER BY category_name')