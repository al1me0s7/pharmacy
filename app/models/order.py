from app.models.database import Database

class Order:
    @staticmethod
    def create(user_id, delivery_address, delivery_method, total, comment='', payment_method='cash_on_delivery', city_name=None):
        # CRUD: Створити замовлення (INSERT)
        return Database.execute(
            'INSERT INTO orders (user_id, delivery_address, delivery_method, total_sum, comment, payment_method, city_name) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING order_id',
            (user_id, delivery_address, delivery_method, total, comment, payment_method, city_name),
            returning=True
        )
    
    @staticmethod
    # CRUD: Додати ліки до замовлення (INSERT або UPDATE при конфлікті)
    def add_medicine(order_id, medicine_id, quantity, price, subtotal):
        Database.execute(
        '''INSERT INTO order_medicine (order_id, medicine_id, quantity, price_at_purchase, subtotal) 
           VALUES (%s,%s,%s,%s,%s)
           ON CONFLICT (order_id, medicine_id)
           DO UPDATE SET quantity = order_medicine.quantity + EXCLUDED.quantity,
                         subtotal = order_medicine.subtotal + EXCLUDED.subtotal''',
        (order_id, medicine_id, quantity, price, subtotal)
    )
    
    @staticmethod
    def get_by_user(user_id):
        # CRUD: Отримати замовлення користувача (SELECT WHERE ORDER BY)
        return Database.fetchall('SELECT * FROM orders WHERE user_id = %s ORDER BY order_date DESC', (user_id,))
    
    @staticmethod
    def get_by_id(order_id):
        # CRUD: Знайти замовлення за ID (SELECT WHERE)
        return Database.fetchone('SELECT * FROM orders WHERE order_id = %s', (order_id,))
    
    @staticmethod
    def get_items(order_id):
        # CRUD: Знайти - отримання товарів замовлення
        return Database.fetchall(
            'SELECT om.*, m.name FROM order_medicine om JOIN medicines m ON om.medicine_id=m.medicine_id WHERE om.order_id=%s',
            (order_id,)
        )
    
    @staticmethod
    def delete(order_id):
        # CRUD: Видалити замовлення (DELETE CASCADE)
        Database.execute('DELETE FROM orders WHERE order_id=%s', (order_id,))