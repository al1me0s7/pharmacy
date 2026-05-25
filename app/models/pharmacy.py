from app.models.database import Database

class Pharmacy:
    @staticmethod
    def get_all():
        # CRUD: Отримати всі аптеки (SELECT ORDER BY) з JOIN на міста для отримання city_name
        return Database.fetchall('''SELECT p.*, c.city_name FROM pharmacies p 
                                     LEFT JOIN cities c ON p.city_id = c.city_id 
                                     ORDER BY p.pharmacy_name''')
    
    @staticmethod
    def get_by_city(city_id):
        # CRUD: Знайти - отримання аптек за містом
        return Database.fetchall('SELECT * FROM pharmacies WHERE city_id=%s ORDER BY pharmacy_name', (city_id,))
    
    @staticmethod
    def get_by_id(pharmacy_id):
        # CRUD: Знайти аптеку за ID (SELECT WHERE)
        return Database.fetchone('SELECT * FROM pharmacies WHERE pharmacy_id=%s', (pharmacy_id,))
    
    @staticmethod
    def get_inventory(pharmacy_id, search_query=None):
        # CRUD: Знайти - отримання інвентарю аптеки
        sql = '''SELECT i.quantity, i.selling_price as price, m.* 
                 FROM inventory i 
                 JOIN medicines m ON i.medicine_id=m.medicine_id 
                 WHERE i.pharmacy_id=%s'''
        params = [pharmacy_id]
        if search_query:
            sql += ' AND m.name ILIKE %s'
            params.append(f'%{search_query}%')
        sql += ' ORDER BY m.name'
        return Database.fetchall(sql, tuple(params))