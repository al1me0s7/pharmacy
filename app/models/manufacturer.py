from app.models.database import Database

class Manufacturer:
    @staticmethod
    def get_all():
        # CRUD: Отримати всіх виробників (SELECT ORDER BY)
        return Database.fetchall('SELECT * FROM manufacturers ORDER BY manufacturer_name')