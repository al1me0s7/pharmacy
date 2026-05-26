from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from app.utils.helpers import get_current_user, can_cancel_order_or_booking
from app.models import Booking, Medicine, Pharmacy, City, User, Database
from app.utils.pdf_generator import generate_booking_pdf, generate_multi_booking_pdf
from datetime import datetime, timedelta
import json

bp = Blueprint('bookings', __name__)

# Додати ліки до корзини бронювань
@bp.route('/bookings/cart/add', methods=['POST'])
def bookings_cart_add():
    mid = request.form.get('medicine_id') or request.args.get('medicine_id')
    qty = int(request.form.get('quantity', 1))
    if not mid:
        return redirect(url_for('main.index'))
    med = Medicine.get_by_id(mid)
    if not med:
        flash('Препарат не знайдено', 'error')
        return redirect(request.referrer or url_for('main.index'))
    booking_cart = session.get('booking_cart', {})
    existing = booking_cart.get(str(mid), 0)
    try:
        existing = int(existing)
    except:
        existing = 0
    booking_cart[str(mid)] = existing + qty
    session['booking_cart'] = booking_cart
    flash(f'✓ "{med.get("name")}" додано до корзини бронювань!', 'success')
    return redirect(request.referrer or url_for('main.index'))
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from app.utils.helpers import get_current_user, can_cancel_order_or_booking
from app.models import Booking, Medicine, Pharmacy, City, User, Database
from app.utils.pdf_generator import generate_booking_pdf, generate_multi_booking_pdf
from datetime import datetime, timedelta
import json

bp = Blueprint('bookings', __name__)

# CRUD: Створити - корзина для бронюванн
@bp.route('/bookings/cart')
def bookings_cart():
    """Перегляд корзини бронювань"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.register', next='/bookings/cart'))
    
    booking_cart = session.get('booking_cart', {})
    items = []
    total = 0.0
    
    for mid, qty in booking_cart.items():
        try:
            med = Medicine.get_by_id(int(mid))
            if med:
                unit_price = float(med.get('price', 0))
                subtotal = unit_price * int(qty)
                items.append({
                    'medicine': med,
                    'quantity': int(qty),
                    'unit_price': unit_price,
                    'subtotal': subtotal,
                    'medicine_id': int(mid)
                })
                total += subtotal
        except:
            pass
    
    return render_template('booking_cart.html', items=items, total=total)

# CRUD: Видалити з корзини бронювань
@bp.route('/bookings/cart/remove/<int:mid>', methods=['POST'])
def bookings_cart_remove(mid):
    """Видалити лік з корзини бронювань"""
    booking_cart = session.get('booking_cart', {})
    if str(mid) in booking_cart:
        del booking_cart[str(mid)]
    session['booking_cart'] = booking_cart
    return redirect(url_for('bookings.bookings_cart'))

# CRUD: Оновити корзину бронювань
@bp.route('/bookings/cart/update', methods=['POST'])
def bookings_cart_update():
    """Оновити кількість в корзині бронювань"""
    booking_cart = session.get('booking_cart', {})
    
    if request.is_json:
        data = request.get_json()
        for item in data.get('items', []):
            mid = str(item.get('mid'))
            qty = int(item.get('qty', 0))
            if qty > 0:
                booking_cart[mid] = qty
            else:
                booking_cart.pop(mid, None)
        session['booking_cart'] = booking_cart
    
    return jsonify({'success': True})

# CRUD: Оформити бронювання з корзини
@bp.route('/bookings/checkout', methods=['GET', 'POST'])
def bookings_checkout():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.register', next='/bookings/checkout'))
    
    booking_cart = session.get('booking_cart', {})
    if not booking_cart:
        flash('Корзина бронювань порожня', 'info')
        return redirect(url_for('bookings.bookings_cart'))
    
    # Зібрати інформацію про ліки в корзині
    items = []
    total = 0.0
    for mid, qty in booking_cart.items():
        try:
            med = Medicine.get_by_id(int(mid))
            if med:
                unit_price = float(med.get('price', 0))
                subtotal = unit_price * int(qty)
                items.append({
                    'medicine': med,
                    'medicine_id': int(mid),
                    'quantity': int(qty),
                    'unit_price': unit_price,
                    'subtotal': subtotal
                })
                total += subtotal
        except:
            pass
    
    if not items:
        flash('Немає корзктних позицій', 'error')
        return redirect(url_for('bookings.bookings_cart'))
    
    if request.method == 'POST':
        pharmacy_id = request.form.get('pharmacy')
        if not pharmacy_id:
            flash('Будь ласка, оберіть аптеку для отримання', 'error')
            return redirect(url_for('bookings.bookings_checkout'))
        
        try:
            pharmacy_id = int(pharmacy_id)
            pharmacy = Pharmacy.get_by_id(pharmacy_id)
            if not pharmacy:
                flash('Аптеку не знайдено', 'error')
                return redirect(url_for('bookings.bookings_checkout'))
            
            # Створити бронювання з множественими лікам
            pickup_deadline = datetime.now() + timedelta(hours=24)
 
            items_json_data = []
            for item in items:
                med_id = item['medicine_id']
                # Отримати ціну з inventory
                inv_row = Database.fetchone('SELECT selling_price FROM inventory WHERE medicine_id = %s AND pharmacy_id = %s', (med_id, pharmacy_id))
                unit_price = float(inv_row.get('selling_price')) if inv_row and inv_row.get('selling_price') is not None else float(item['medicine'].get('price', 0))
                items_json_data.append({
                    'medicine_id': med_id,
                    'name': item['medicine'].get('name'),
                    'quantity': item['quantity'],
                    'unit_price': unit_price,
                    'pharmacy_id': pharmacy_id
                })
            
            items_json = json.dumps(items_json_data, ensure_ascii=False)
            bid = Booking.create_with_items(user['user_id'], pharmacy_id, pickup_deadline.isoformat(), items_json, total)
            
            # Додати ліки до booking_items таблиці
            for item in items:
                Booking.add_items(bid, [(item['medicine_id'], item['quantity'], item['unit_price'])])
            
            # Очистити корзину бронювань
            session.pop('booking_cart', None)
            session['last_booking_id'] = bid
            
            flash('Бронювання успішно створено!', 'success')
            return redirect(url_for('bookings.booking_success', bid=bid))
        except Exception as e:
            flash(f'Помилка при створенні бронювання: {str(e)}', 'error')
            return redirect(url_for('bookings.bookings_checkout'))
    
    pharmacies = Pharmacy.get_all()
    cities = City.get_all()
    
    return render_template('bookings_checkout.html', items=items, total=total, pharmacies=pharmacies, cities=cities)

# CRUD: Успіх бронювання
@bp.route('/bookings/success/<int:bid>')
def booking_success(bid):
    """Сторінка успіху після створення бронювання"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    booking = Booking.get_by_id(bid)
    if not booking or booking['user_id'] != user['user_id']:
        flash('Бронювання не знайдено', 'error')
        return redirect(url_for('main.index'))
    
    # Отримати ліки в бронюванні
    items = Booking.get_items(bid)
    pharmacy = Pharmacy.get_by_id(booking['pharmacy_id'])
    
    return render_template('booking_success.html', booking=booking, items=items, pharmacy=pharmacy)

# CRUD: Створення бронювання
# CRUD: Перегляд моїх бронювань
@bp.route('/my_bookings')
def my_bookings():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.register', next='/my_bookings'))
    
    Booking.update_expired()
    bookings = Booking.get_by_user(user['user_id'])
    
    for booking in bookings:
        booking['can_cancel'] = booking['status'] == 'active' and can_cancel_order_or_booking(booking['booking_date'])
        # CRUD: Відображення статусу бронювання
        booking['status_display'] = 'Активне' if booking.get('status') == 'active' else ('Отримане' if booking.get('status') == 'collected' else 'Закінчилось')
    
    return render_template('my_bookings.html', bookings=bookings)

@bp.route('/bookings/delete/<int:bid>', methods=['POST'])
def booking_delete(bid):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    booking = Booking.get_by_id(bid)
    if not booking or booking['user_id'] != user['user_id']:
        flash('Немає прав на цю дію', 'error')
        return redirect(url_for('profile.profile'))
    
    if booking['status'] != 'active':
        flash('Це бронювання неможливо скасувати', 'error')
        return redirect(url_for('bookings.my_bookings'))
    
    if not can_cancel_order_or_booking(booking['booking_date']):
        flash('Бронювання неможливо скасувати (доступно лише в першу годину після створення)', 'error')
        return redirect(url_for('bookings.my_bookings'))
    
    Booking.delete(bid)
    flash('Бронювання скасовано')
    return redirect(url_for('bookings.my_bookings'))

@bp.route('/bookings/confirm/<int:bid>', methods=['POST'])
def booking_confirm(bid):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    booking = Booking.get_by_id(bid)
    if not booking or booking['user_id'] != user['user_id']:
        flash('Немає прав на цю дію', 'error')
        return redirect(url_for('profile.profile'))
    
    Booking.update_status(bid, 'collected')
    flash('Бронювання помічено як отримане')
    return redirect(url_for('bookings.my_bookings'))

@bp.route('/bookings/poll')
def bookings_poll():
    user = get_current_user()
    if not user:
        return jsonify({}), 401
    
    Booking.update_expired()
    bookings = Booking.get_by_user(user['user_id'])
    
    result_bookings = []
    for b in bookings:
        # Якщо це стара одно-ліпкова бронь, показуємо що раніш
        if b.get('medicine_id'):
            med = Database.fetchone('SELECT name FROM medicines WHERE medicine_id=%s', (b['medicine_id'],))
            result_bookings.append({
                'booking_id': b['booking_id'],
                'status': b['status'],
                'medicine_name': med.get('name') if med else 'Unknown',
                'pharmacy_name': Database.fetchone('SELECT pharmacy_name FROM pharmacies WHERE pharmacy_id=%s', (b['pharmacy_id'],)).get('pharmacy_name') if b['pharmacy_id'] else ''
            })
        # Якщо це нова багато-ліпкова бронь з items
        elif b.get('items'):
            try:
                items_data = json.loads(b.get('items', '[]'))
                items_str = ', '.join([f"{item.get('name')} ({item.get('quantity')}шт)" for item in items_data])
            except:
                items_str = 'Множественные товары'
            result_bookings.append({
                'booking_id': b['booking_id'],
                'status': b['status'],
                'medicine_name': items_str,
                'pharmacy_name': Database.fetchone('SELECT pharmacy_name FROM pharmacies WHERE pharmacy_id=%s', (b['pharmacy_id'],)).get('pharmacy_name') if b['pharmacy_id'] else ''
            })
    
    return jsonify({'bookings': result_bookings})

# CRUD: Завантажити - завантаження PDF чека бронювання
@bp.route('/download_booking/<int:bid>')
def download_booking(bid):
    user = get_current_user()
    if not user:
        return 'Unauthorized', 401
    
    booking = Booking.get_by_id(bid)
    if not booking or booking['user_id'] != user['user_id']:
        return 'Not Found', 404

    if booking['status'] == 'expired':
        return 'Forbidden - booking expired', 403
    
    user_obj = User.find_by_id(booking['user_id'])
    pharmacy = Pharmacy.get_by_id(booking['pharmacy_id']) if booking.get('pharmacy_id') else None
    
    # Якщо аптека не знайдена — підставити заглушку
    if not pharmacy:
        pharmacy = {'pharmacy_name': 'Невідома аптека', 'address': 'N/A', 'city_id': None, 'phone': 'N/A'}
    
    city = City.get_by_id(pharmacy['city_id']) if pharmacy.get('city_id') else None
    if not city:
        city = {'city_name': 'N/A'}

    try:
        if booking.get('items'):
            items_data = json.loads(booking.get('items', '[]'))
            pdf_buffer = generate_multi_booking_pdf(booking, user_obj, items_data, pharmacy, city)
        else:
            medicine = Medicine.get_by_id(booking['medicine_id']) if booking.get('medicine_id') else None
            if not medicine:
                medicine = {'name': 'Невідомий препарат', 'price': 0}
            pdf_buffer = generate_booking_pdf(booking, user_obj, medicine, pharmacy, city)
    except Exception as e:
        return f'Помилка генерації PDF: {str(e)}', 500
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'booking_{bid}.pdf'
    )