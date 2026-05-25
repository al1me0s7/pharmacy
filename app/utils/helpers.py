from flask import session
from app.models import Database, User, Medicine, Pharmacy, City
from datetime import datetime, timedelta

# отримання поточного користувача
def get_current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return User.find_by_id(uid)

# перевірка чи є користувач адміністратором
def is_admin(user):
    return user and user.get('role') == 'admin'

# отримання товарів у кошику
def get_cart_items():
    cart = session.get('cart', {})
    if not cart:
        return [], 0
    parsed = []
    ids = set()
    for k, v in cart.items():
        if isinstance(v, dict):
            mid = int(v.get('medicine_id'))
            pid = v.get('pharmacy_id')
            qty = int(v.get('quantity', 1))
        else:
            if ':' in k:
                mid_str, pid_str = k.split(':', 1)
                mid = int(mid_str)
                pid = int(pid_str) if pid_str else None
            else:
                mid = int(k.split('_')[0])
                pid = None
            try:
                qty = int(v)
            except:
                qty = 1

        parsed.append({'medicine_id': mid, 'pharmacy_id': pid, 'quantity': qty, 'key': k})
        ids.add(mid)

    # отримання інформації про ліки
    meds = Medicine.get_by_ids(list(ids)) if ids else []
    meds_map = {m['medicine_id']: m for m in meds}

    items = []
    total = 0.0
    for p in parsed:
        m = meds_map.get(p['medicine_id'])
        if not m:
            continue
        unit_price = m.get('price', 0.0)
        if p.get('pharmacy_id'):
            # отримання ціни з inventory
            inv_row = Database.fetchone('SELECT selling_price FROM inventory WHERE medicine_id=%s AND pharmacy_id=%s', (p['medicine_id'], p['pharmacy_id']))
            if inv_row and inv_row.get('selling_price') is not None:
                try:
                    unit_price = float(inv_row.get('selling_price'))
                except:
                    pass

        # обчислення підсумку
        qty = p.get('quantity', 1)
        subtotal = float(unit_price) * int(qty)
        total += subtotal
        items.append({
            'medicine': m,
            'quantity': int(qty),
            'unit_price': float(unit_price),
            'subtotal': subtotal,
            'pharmacy_id': p.get('pharmacy_id'),
            'key': p.get('key')
        })

    return items, total

def update_order_statuses():
    now = datetime.now()
    
    #  автоматичне оновлення статусів замовлень (confirmed)
    Database.execute("""
        UPDATE orders 
        SET delivery_status = 'confirmed' 
        WHERE delivery_status = 'pending' 
        AND order_date < %s
    """, (now - timedelta(minutes=30),))
    
    # автоматичне оновлення статусів замовлень (shipped)
    Database.execute("""
        UPDATE orders 
        SET delivery_status = 'shipped' 
        WHERE delivery_status = 'confirmed' 
        AND order_date < %s
    """, (now - timedelta(minutes=60),))
    
    # автоматичне оновлення статусів замовлень (delivered)
    Database.execute("""
        UPDATE orders 
        SET delivery_status = 'delivered' 
        WHERE delivery_status = 'shipped' 
        AND order_date < %s
    """, (now - timedelta(minutes=90),))

def translate_delivery_method(method):
    translations = {
        'home': 'Доставка додому',
        'self_pickup': 'Доставка з аптеки',
        'delivery_from_pharmacy': 'Доставка з аптеки',
        'post_nova': 'Нова Пошта',
        'post_ukr': 'Укрпошта',
        'post': 'Пошта'
    }
    return translations.get(method, method)

# переклад статусу замовлення
def translate_order_status(status):
    translations = {
        'pending': 'Очікує',
        'confirmed': 'Підтверджено',
        'shipped': 'Відправлено',
        'delivered': 'Доставлено',
        'received': 'Отримано',
        'collected': 'Отримано',
        'cancelled': 'Скасовано'
    }
    return translations.get(status, status)

# перевірка чи можна скасувати замовлення або бронювання
def can_cancel_order_or_booking(date_str, status=None):
    if status in ('shipped', 'delivered'):
        return False
    try:
        if not date_str:
            return False
        if hasattr(date_str, 'tzinfo') or isinstance(date_str, datetime):
            order_date = date_str
        else:
            order_date = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))

        now = datetime.now(order_date.tzinfo) if order_date.tzinfo else datetime.now()
        return now - order_date < timedelta(hours=1)
    except Exception:
        return False