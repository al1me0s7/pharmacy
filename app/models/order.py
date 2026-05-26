from app.models.database import Database

class Order:
    @staticmethod
    def create(user_id, delivery_address, delivery_method, total, comment='', payment_method='cash_on_delivery', city_name=None):
        return Database.execute(
            'INSERT INTO orders (user_id, delivery_address, delivery_method, total_sum, comment, payment_method, city_name) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING order_id',
            (user_id, delivery_address, delivery_method, total, comment, payment_method, city_name),
            returning=True
        )
    
    @staticmethod
    def add_medicine(order_id, medicine_id, quantity, price, subtotal):
        Database.execute(
            '''INSERT INTO order_medicine (order_id, medicine_id, quantity, price_at_purchase, subtotal) 
               VALUES (%s,%s,%s,%s,%s)''',
            (order_id, medicine_id, quantity, price, subtotal)
        )
    
    @staticmethod
    def get_by_user(user_id):
        return Database.fetchall('SELECT * FROM orders WHERE user_id = %s ORDER BY order_date DESC', (user_id,))
    
    @staticmethod
    def get_by_id(order_id):
        return Database.fetchone('SELECT * FROM orders WHERE order_id = %s', (order_id,))
    
    @staticmethod
    def get_items(order_id):
        return Database.fetchall(
            'SELECT om.*, m.name FROM order_medicine om JOIN medicines m ON om.medicine_id=m.medicine_id WHERE om.order_id=%s',
            (order_id,)
        )
    
    @staticmethod
    def delete(order_id):
        Database.execute('DELETE FROM orders WHERE order_id=%s', (order_id,))