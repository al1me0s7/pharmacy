from app.models.database import Database

class Statistics:
    @staticmethod
    def total_orders():
        result = Database.fetchone('SELECT COUNT(*) as cnt FROM orders')
        return result['cnt'] if result else 0
    
    @staticmethod
    def total_bookings():
        result = Database.fetchone('SELECT COUNT(*) as cnt FROM bookings')
        return result['cnt'] if result else 0
    
    @staticmethod
    def average_order():
        result = Database.fetchone('SELECT COALESCE(AVG(total_sum),0) as avg FROM orders')
        return result['avg'] if result else 0
    
    @staticmethod
    def top_medicines(limit=5):
        return Database.fetchall(
            '''SELECT m.name, SUM(om.quantity) as sold 
               FROM order_medicine om 
               JOIN medicines m ON om.medicine_id=m.medicine_id 
               GROUP BY m.medicine_id, m.name
               ORDER BY sold DESC 
               LIMIT %s''',
            (limit,)
        )
    
    @staticmethod
    def bookings_per_pharmacy():
        return Database.fetchall(
            '''SELECT p.pharmacy_name, COUNT(*) as cnt 
               FROM bookings b 
               JOIN pharmacies p ON b.pharmacy_id=p.pharmacy_id 
               GROUP BY p.pharmacy_id, p.pharmacy_name
               ORDER BY cnt DESC'''
        )