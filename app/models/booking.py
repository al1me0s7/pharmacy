from app.models.database import Database
import datetime
import json

class Booking:
    @staticmethod
    def create(user_id, medicine_id, pharmacy_id, pickup_deadline):
        return Database.execute(
            'INSERT INTO bookings (user_id, medicine_id, pharmacy_id, pickup_deadline) VALUES (%s,%s,%s,%s) RETURNING booking_id',
            (user_id, medicine_id, pharmacy_id, pickup_deadline),
            returning=True
        )
    
    @staticmethod
    def create_with_items(user_id, pharmacy_id, pickup_deadline, items_json, total_sum=0):
        return Database.execute(
            'INSERT INTO bookings (user_id, pharmacy_id, pickup_deadline, items, status) VALUES (%s,%s,%s,%s,%s) RETURNING booking_id',
            (user_id, pharmacy_id, pickup_deadline, items_json, 'pending'),
            returning=True
        )

    @staticmethod
    def add_items(booking_id, items_list):
        # booking_items таблиці немає — дані зберігаються в JSON колонці items
        pass

    @staticmethod
    def get_items(booking_id):
        booking = Database.fetchone('SELECT items FROM bookings WHERE booking_id=%s', (booking_id,))
        if not booking or not booking.get('items'):
            return []
        try:
            items_data = json.loads(booking['items'])
            return [
                {
                    'medicine_id': item.get('medicine_id'),
                    'name': item.get('name'),
                    'quantity': item.get('quantity'),
                    'price_at_booking': item.get('unit_price'),
                    'subtotal': item.get('quantity', 0) * item.get('unit_price', 0)
                }
                for item in items_data
            ]
        except Exception:
            return []

    @staticmethod
    def get_by_user(user_id):
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
        return Database.fetchone('SELECT * FROM bookings WHERE booking_id=%s', (booking_id,))
    
    @staticmethod
    def update_status(booking_id, status):
        Database.execute('UPDATE bookings SET status=%s WHERE booking_id=%s', (status, booking_id))
    
    @staticmethod
    def delete(booking_id):
        Database.execute('DELETE FROM bookings WHERE booking_id=%s', (booking_id,))
    
    @staticmethod
    def update_expired():
        now = datetime.datetime.now()
        Database.execute(
            "UPDATE bookings SET status=%s WHERE status=%s AND pickup_deadline < %s",
            ('expired', 'active', now)
        )