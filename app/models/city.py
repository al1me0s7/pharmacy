from app.models.database import Database

class City:
    @staticmethod
    def get_all():
        return Database.fetchall('SELECT * FROM cities ORDER BY city_name ASC')
    
    @staticmethod
    def get_by_id(city_id):
        return Database.fetchone('SELECT * FROM cities WHERE city_id = %s', (city_id,))