from app.models.database import Database
import datetime
import json

class Booking:
    @staticmethod
    def create(user_id, medicine_id, pharmacy_id, pickup_deadline):
        # CRUD: Створити бронювання (INSERT)
        return Database.execute(
            'INSERT INTO bookings (user_id, medicine_id, pharmacy_id, pickup_deadline) VALUES (%s,%s,%s,%s) RETURNING booking_id',
            (user_id, medicine_id, pharmacy_id, pickup_deadline),
            returning=True
        )
    
    @staticmethod
    def create_with_items(user_id, pharmacy_id, pickup_deadline, items_json, total_sum=0):
        # CRUD: Створити бронювання з кількома лікам (INSERT)
        return Database.execute(
            'INSERT INTO bookings (user_id, pharmacy_id, pickup_deadline, items, status) VALUES (%s,%s,%s,%s,%s) RETURNING booking_id',
            (user_id, pharmacy_id, pickup_deadline, items_json, 'pending'),
            returning=True
        )
    
    @staticmethod
    def add_items(booking_id, items_list):
        """Додати ліки до бронювання. items_list = [(medicine_id, quantity, price_at_booking), ...]"""
        for medicine_id, quantity, price_at_booking in items_list:
            Database.execute(
                'INSERT INTO booking_items (booking_id, medicine_id, quantity, price_at_booking) VALUES (%s,%s,%s,%s) ON CONFLICT (booking_id, medicine_id) DO UPDATE SET quantity = booking_items.quantity + EXCLUDED.quantity',
                (booking_id, medicine_id, quantity, price_at_booking)
            )
    
    @staticmethod
    def get_items(booking_id):
        """Отримати всі ліки в бронюванні"""
        return Database.fetchall(
            '''SELECT bi.medicine_id, m.name, bi.quantity, bi.price_at_booking, (bi.quantity * bi.price_at_booking) as subtotal
               FROM booking_items bi
               JOIN medicines m ON bi.medicine_id = m.medicine_id
               WHERE bi.booking_id = %s
               ORDER BY m.name''',
            (booking_id,)
        )
    
    @staticmethod
    def get_by_user(user_id):
        # CRUD: Отримати бронювання користувача (SELECT JOIN ORDER BY)
        return Database.fetchall(
            '''SELECT b.*, p.pharmacy_name 
               FROM bookings b 
               LEFT JOIN pharmacies p ON b.pharmacy_id=p.pharmacy_id 
               WHERE b.user_id=%s 
               ORDER BY b.booking_date DESC''',
            (user_id,)
        )
    
    @staticmethod
    def get_by_id(booking_id):
        # CRUD: Знайти бронювання за ID (SELECT WHERE)
        return Database.fetchone('SELECT * FROM bookings WHERE booking_id=%s', (booking_id,))
    
    @staticmethod
    def update_status(booking_id, status):
        # CRUD: Оновити статус бронювання (UPDATE)
        Database.execute('UPDATE bookings SET status=%s WHERE booking_id=%s', (status, booking_id))
    
    @staticmethod
    def delete(booking_id):
        # CRUD: Видалити бронювання (DELETE)
        Database.execute('DELETE FROM bookings WHERE booking_id=%s', (booking_id,))
    
    @staticmethod
    def update_expired():
        # CRUD: Оновити - оновлення прострочених бронювань
        now = datetime.datetime.now()
        Database.execute(
            "UPDATE bookings SET status=%s WHERE status=%s AND pickup_deadline < %s",
            ('expired', 'active', now)
        )