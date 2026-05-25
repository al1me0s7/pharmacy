from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from app.utils.helpers import get_current_user, update_order_statuses, can_cancel_order_or_booking
from app.models import Order, Database, Pharmacy, City, User, Booking
from app.utils.pdf_generator import generate_order_pdf, generate_payment_receipt_pdf
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

bp = Blueprint('orders', __name__)
# CRUD: Створити - оформлення замовлення з кошика
@bp.route('/cart/checkout', methods=['GET', 'POST'])
def cart_checkout():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.register', next='/cart/checkout'))
    
    from app.utils.helpers import get_cart_items
    # Accept pharmacy selection from query string (when coming from cart selection)
    q_pharmacy = request.args.get('pharmacy')
    if q_pharmacy:
        try:
            session['selected_pharmacy_id'] = int(q_pharmacy)
            # try to set city as well
            try:
                ph = Pharmacy.get_by_id(int(q_pharmacy))
                if ph and ph.get('city_id'):
                    session['selected_city_id'] = str(ph.get('city_id'))
            except Exception:
                pass
        except Exception:
            pass

    temp_cart = None
    if q_pharmacy:
        try:
            pid = int(q_pharmacy)
            cart = session.get('cart', {}) or {}
            updated_cart = {}
            for key, qty in cart.items():
                if ':' not in key or (':' in key and key.split(':',1)[1] == ''):
                    updated_cart[f'{key.split(':',1)[0]}:{pid}'] = qty
                else:
                    updated_cart[key] = qty
            temp_cart = cart
            session['cart'] = updated_cart
        except Exception:
            temp_cart = None

    items, total = get_cart_items()

    if not items:
        flash('Кошик порожній')
        return redirect(url_for('main.index'))
    

    has_prescription = any(i['medicine'].get('prescription_required') for i in items)
    has_non_prescription = any(not i['medicine'].get('prescription_required') for i in items)
    
    if has_prescription and has_non_prescription:
        order_type = 'mixed'
        is_mixed_order = True
    elif has_prescription:
        order_type = 'booking'
        is_mixed_order = False
    else:
        order_type = 'site'
        is_mixed_order = False
    
    pharmacy = None
    city_name = ''

    if request.method == 'POST':
        items, total = get_cart_items()
        if not items:
            flash('Кошик порожній')
            return redirect(url_for('cart.cart_view'))

        delivery_method = request.form.get('delivery_method', 'home')
        payment_method = request.form.get('payment_method', 'cash_on_delivery')
        user_comment = request.form.get('comment', '').strip()
        city_from_form = request.form.get('city', '').strip() or user.get('city_name') or ''
        
        # рецептурні препарати - створюємо бронювання
        if is_mixed_order or order_type == 'booking':
            # тільки самовивіз і оплата при отриманні
            if delivery_method != 'self_pickup':
                flash('Коли у замовленні є рецептурні препарати, доступний тільки самовивіз з аптеки!', 'error')
                return redirect(url_for('orders.cart_checkout'))
            if payment_method != 'cash_on_delivery':
                flash('Для замовлень з рецептурними препаратами доступна тільки оплата при отриманні!', 'error')
                return redirect(url_for('orders.cart_checkout'))
            
            # Вибір аптеки для самовивізу рецептурних препаратів - використовуємо ціни з цієї аптеки
            pharmacy_id = request.form.get('pharmacy')
            if not pharmacy_id:
                flash('Будь ласка, оберіть аптеку для самовивізу рецептурних препаратів', 'error')
                return redirect(url_for('orders.cart_checkout'))
            
            pharmacy = Pharmacy.get_by_id(pharmacy_id)
            if not pharmacy:
                flash('Аптеку не знайдено', 'error')
                return redirect(url_for('orders.cart_checkout'))
            
            delivery_address = pharmacy.get('pharmacy_name', '')
            comment = user_comment or f"Самовивіз з аптеки {pharmacy.get('pharmacy_name')}. ВАЖЛИВО: Рецептурні препарати видаються тільки при наявності рецепту!"
            
            # Створюємо бронювання
            from datetime import timedelta
            import json
            try:
                pickup_deadline = datetime.now() + timedelta(hours=24)
                booking_items = []
                for it in items:
                    med_id = it['medicine']['medicine_id']
                    # Отримати ціну з inventory
                    inv_row = Database.fetchone('SELECT selling_price FROM inventory WHERE medicine_id = %s AND pharmacy_id = %s', (med_id, pharmacy_id))
                    unit_price = float(inv_row.get('selling_price')) if inv_row and inv_row.get('selling_price') is not None else float(it['medicine'].get('price', 0))
                    
                    booking_items.append({
                        'medicine_id': int(med_id),
                        'name': it['medicine'].get('name'),
                        'quantity': int(it['quantity']),
                        'unit_price': unit_price,
                        'pharmacy_id': int(pharmacy_id)
                    })
                
                items_json = json.dumps(booking_items, ensure_ascii=False)
                bid = Booking.create_with_items(user['user_id'], int(pharmacy_id), pickup_deadline.isoformat(), items_json, float(total))
                # Додати записи в booking_items таблицю для сумісності (може не існувати)
                try:
                    for item in items:
                        med_id = item['medicine'].get('medicine_id')
                        qty = item.get('quantity', 1)
                        price = item['medicine'].get('price', 0)
                        Booking.add_items(bid, [(med_id, qty, price)])
                except Exception as add_items_error:
                    pass
                session.pop('cart', None)
                flash('Бронювання успішно оформлено!', 'success')
                return redirect(url_for('bookings.my_bookings'))
            except Exception as e:
                flash(f'Помилка при створенні бронювання: {str(e)}', 'error')
                return redirect(url_for('cart.cart_view'))
        
        # Звичайне замовлення сайту 
        pharmacy_id = None
        pharmacy = None
        
        if delivery_method == 'home':
            delivery_address = request.form.get('delivery_address', user.get('address', ''))
            city = city_from_form
            if city and city not in delivery_address:
                delivery_address = f"{city}, {delivery_address}"
            comment = user_comment
        elif delivery_method == 'self_pickup':
            # Якщо самовивіз — це бронювання, а не замовлення!
            pharmacy_id = request.form.get('pharmacy')
            if not pharmacy_id:
                flash('Будь ласка, оберіть аптеку для самовивізу', 'error')
                return redirect(url_for('orders.cart_checkout'))
            pharmacy = Pharmacy.get_by_id(pharmacy_id)
            if not pharmacy:
                flash('Аптеку не знайдено', 'error')
                return redirect(url_for('orders.cart_checkout'))
            city = city_from_form or pharmacy.get('city_name') or ''
            delivery_address = pharmacy.get('pharmacy_name', '')
            if city and city not in delivery_address:
                delivery_address = f"{city}, {delivery_address}"
            comment = user_comment or f"Самовивіз з аптеки {pharmacy.get('pharmacy_name')}"
            from datetime import timedelta
            import json
            try:
                pickup_deadline = datetime.now() + timedelta(hours=24)
                booking_items = []
                for it in items:
                    med_id = it['medicine']['medicine_id']
                    inv_row = Database.fetchone('SELECT selling_price FROM inventory WHERE medicine_id = %s AND pharmacy_id = %s', (med_id, pharmacy_id))
                    unit_price = float(inv_row.get('selling_price')) if inv_row and inv_row.get('selling_price') is not None else float(it['medicine'].get('price', 0))
                    booking_items.append({
                        'medicine_id': int(med_id),
                        'name': it['medicine'].get('name'),
                        'quantity': int(it['quantity']),
                        'unit_price': unit_price,
                        'pharmacy_id': int(pharmacy_id)
                    })
                items_json = json.dumps(booking_items, ensure_ascii=False)
                bid = Booking.create_with_items(user['user_id'], int(pharmacy_id), pickup_deadline.isoformat(), items_json, float(total))
                try:
                    for item in items:
                        med_id = item['medicine'].get('medicine_id')
                        qty = item.get('quantity', 1)
                        price = item['medicine'].get('price', 0)
                        Booking.add_items(bid, [(med_id, qty, price)])
                except Exception as add_items_error:
                    pass
                session.pop('cart', None)
                flash('Бронювання успішно оформлено!', 'success')
                return redirect(url_for('bookings.my_bookings'))
            except Exception as e:
                flash(f'Помилка при створенні бронювання: {str(e)}', 'error')
                return redirect(url_for('cart.cart_view'))
        elif delivery_method == 'nova_poshta':
            post_branch = request.form.get('post_branch', '')
            delivery_address = f"Нова Пошта — {post_branch}"
            city = city_from_form
            comment = user_comment
        elif delivery_method == 'ukrposhta':
            post_branch = request.form.get('post_branch', '')
            delivery_address = f"Укрпошта — {post_branch}"
            city = city_from_form
            comment = user_comment
        elif delivery_method == 'address':
            delivery_address = request.form.get('delivery_address', user.get('address', ''))
            city = city_from_form
            comment = user_comment
        else:
            delivery_address = user.get('address', '')
            city = city_from_form
            comment = user_comment

        # Групування товарів за аптеками (або None для звичайних замовлень)
        groups = {}
        for it in items:
            pid = None
            groups.setdefault(pid, []).append(it)

        created_orders = []
        pending_groups = []
        for pid, its in groups.items():
            group_total = 0.0
            recalculated_items = []
            for item in its:
                mid = item['medicine']['medicine_id']
                qty = int(item['quantity'])
                unit_price = float(item.get('unit_price', item['medicine'].get('price', 0)))
                
                # Отримати ціну аптеки, якщо вибрана аптека для самовивізу
                if pharmacy_id:
                    inv_row = Database.fetchone('SELECT selling_price FROM inventory WHERE medicine_id = %s AND pharmacy_id = %s', (mid, pharmacy_id))
                    if inv_row and inv_row.get('selling_price') is not None:
                        unit_price = float(inv_row.get('selling_price'))
                
                subtotal = unit_price * qty
                group_total += subtotal
                recalculated_items.append((mid, qty, unit_price, subtotal))

            group_comment = comment
            if pid:
                group_comment = (group_comment + ' | ' if group_comment else '') + f"Аптека ID:{pid}"
            try:
                group_total = float(Decimal(str(group_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            except Exception:
                group_total = float(round(group_total, 2))
            pending_groups.append({
                'pharmacy_id': pid,
                'group_total': group_total,
                'items': [ {'medicine_id': mid, 'quantity': qty, 'unit_price': unit_price, 'subtotal': subtotal} for (mid, qty, unit_price, subtotal) in recalculated_items ]
            })

            # якщо оплата не онлайн карткою - створюємо замовлення зараз
            if payment_method != 'card_online':
                # Визначаємо місто для збереження
                city_name_to_save = city_from_form
                oid = Order.create(user['user_id'], delivery_address, delivery_method, group_total, group_comment, payment_method, city_name=city_name_to_save)
                try:
                    if pid:
                        Database.execute('UPDATE orders SET pharmacy_id=%s WHERE order_id=%s', (pid, oid))
                except Exception:
                    pass
                created_orders.append(oid)
                # Додати товари до замовлення
                for mid, qty, unit_price, subtotal in recalculated_items:
                    Order.add_medicine(oid, mid, qty, unit_price, subtotal)
                    try:
                        if pid:
                            Database.execute('UPDATE inventory SET quantity = GREATEST(quantity - %s, 0) WHERE medicine_id=%s AND pharmacy_id=%s', (qty, mid, pid))
                        else:
                            Database.execute('UPDATE medicines SET quantity_in_stock = GREATEST(COALESCE(quantity_in_stock,0) - %s, 0) WHERE medicine_id=%s', (qty, mid))
                    except Exception:
                        pass
        
        # якщо оплата онлайн карткою - зберігаємо в сесії для завершення після оплати
        if payment_method == 'card_online':
            city_name_to_save = city_from_form
            session['pending_order'] = {
                'user_id': user['user_id'],
                'delivery_address': delivery_address,
                'delivery_method': delivery_method,
                'comment': comment,
                'payment_method': payment_method,
                'groups': pending_groups,
                'city_name': city_name_to_save
            }
            # перенаправляємо на сторінку оплати
            return redirect(url_for('orders.order_payment', oid=0))

        # фіналізуємо замовлення
        session.pop('cart', None)
        session['last_created_orders'] = created_orders
        flash('Замовлення успішно оформлено!')
        if len(created_orders) == 1:
            return redirect(url_for('orders.order_success', oid=created_orders[0]))
        else:
            return redirect(url_for('orders.order_success_multi'))
    
    cities = City.get_all()
    pharmacies = Pharmacy.get_all()

    # Отримати унікальні міста з аптек для вибору
    unique_cities = []
    seen_cities = set()
    for p in pharmacies:
        city_name = p.get('city_name')
        if city_name and city_name not in seen_cities:
            unique_cities.append({'city_name': city_name})
            seen_cities.add(city_name)
    
    # Отримати ціни по аптеках для всіх товарів у кошику через inventory
    pharmacy_prices = {}
    for item in items:
        medicine_id = item.get('medicine', {}).get('medicine_id') or item.get('medicine_id')
        if not medicine_id:
            continue
        prices = Database.fetchall(
            'SELECT pharmacy_id, selling_price FROM inventory WHERE medicine_id = %s',
            (medicine_id,)
        )
        if prices:
            pharmacy_prices[str(medicine_id)] = {str(p.get('pharmacy_id')): float(p.get('selling_price')) for p in prices if p.get('selling_price') is not None}
    
    return render_template(
        'checkout.html',
        items=items,
        total=total,
        user=user,
        cities=unique_cities,
        pharmacies=pharmacies,
        pharmacy_prices=pharmacy_prices,
        order_type=order_type,
        pharmacy=pharmacy,
        city_name=city_name,
        has_prescription=has_prescription
    )
# Відобразити - сторінка успішного оформлення замовлення
@bp.route('/order/success/<int:oid>')
def order_success(oid):
    order = Order.get_by_id(oid)
    items = Order.get_items(oid)
    
    if not order:
        return 'Замовлення не знайдено', 404
    
    pharmacy_obj = None
    try:
        pid = order.get('pharmacy_id')
        if pid:
            pharmacy_obj = Pharmacy.get_by_id(pid)
    except Exception:
        pharmacy_obj = None

    if pharmacy_obj and pharmacy_obj.get('city_id'):
        try:
            city = City.get_by_id(pharmacy_obj.get('city_id'))
            if city:
                pharmacy_obj['city_name'] = city.get('city_name')
        except Exception:
            pass

    can_cancel = can_cancel_order_or_booking(order['order_date'], order['delivery_status'])

    return render_template('order_success.html', order=order, items=items, pharmacy=pharmacy_obj, can_cancel=can_cancel)
# Відобразити - сторінка успішного оформлення кількох замовлень
@bp.route('/order/success/multi')
def order_success_multi():
    oids = session.get('last_created_orders', [])
    if not oids:
        return redirect(url_for('main.index'))
    orders = []
    for oid in oids:
        order = Order.get_by_id(oid)
        if order:
            order['can_cancel'] = can_cancel_order_or_booking(order['order_date'], order['delivery_status'])
            orders.append(order)
    return render_template('order_success_multi.html', orders=orders)

# CRUD: Створити - оплата замовлення онлайн карткою
@bp.route('/order/payment/<int:oid>', methods=['GET', 'POST'])
def order_payment(oid):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    pending = session.get('pending_order')
    order = None
    if not pending:
        order = Order.get_by_id(oid)
        if not order or order['user_id'] != user['user_id']:
            return 'Замовлення не знайдено', 404
        if order.get('payment_method') != 'card_online':
            return redirect(url_for('orders.order_success', oid=oid))

    # обчислити загальну суму
    if request.method == 'POST':
        if pending:
            try:
                total = float(sum(float(g.get('group_total', 0)) for g in pending.get('groups', [])))
            except Exception:
                total = 0.0
        else:
            items = Order.get_items(oid)
            try:
                total = float(order.get('total_sum') or sum(float(item['subtotal']) for item in items))
            except Exception:
                total = sum(float(item['subtotal']) for item in items)

        # обробка форми оплати
        card_number = request.form.get('card_number', '').replace(' ', '')
        expiry_date = request.form.get('expiry_date', '')
        cvv = request.form.get('cvv', '')

        if not card_number or not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            flash('Невірний номер карти', 'error')
            return render_template('payment.html', order_id=oid, total=total)

        if not expiry_date or '/' not in expiry_date:
            flash('Невірний термін дії', 'error')
            return render_template('payment.html', order_id=oid, total=total)

        try:
            month, year = expiry_date.split('/')
            month = int(month)
            year = int('20' + year)
            current_year = datetime.now().year
            current_month = datetime.now().month
            if month < 1 or month > 12:
                flash('Невірний місяць', 'error')
                return render_template('payment.html', order_id=oid, total=total)
            if year < current_year or (year == current_year and month < current_month):
                flash('Термін дії карти минув', 'error')
                return render_template('payment.html', order_id=oid, total=total)
        except Exception:
            flash('Невірний формат терміну дії', 'error')
            return render_template('payment.html', order_id=oid, total=total)

        if not cvv or not cvv.isdigit() or len(cvv) != 3:
            flash('✗ Невірний CVV', 'error')
            return render_template('payment.html', order_id=oid, total=total)

        masked_card = '**** **** **** ' + card_number[-4:] if len(card_number) >= 4 else '**** **** **** ****'
        session['payment_data'] = {
            'order_id': oid,
            'masked_card': masked_card,
            'expiry_date': expiry_date,
            'total': total
        }

        # якщо є відкладене замовлення - створюємо його зараз
        if pending:
            created_orders = []
            try:
                for g in pending.get('groups', []):
                    pid = g.get('pharmacy_id')
                    group_total = float(g.get('group_total', 0))
                    try:
                        group_total = float(Decimal(str(group_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                    except Exception:
                        group_total = float(round(group_total, 2))
                    city_name_to_save = pending.get('city_name')
                    oid_new = Order.create(user['user_id'], pending.get('delivery_address'), pending.get('delivery_method'), group_total, pending.get('comment', ''), pending.get('payment_method'), city_name=city_name_to_save)
                    try:
                        if pid:
                            Database.execute('UPDATE orders SET pharmacy_id=%s WHERE order_id=%s', (pid, oid_new))
                    except Exception:
                        pass
                    created_orders.append(oid_new)
                    for it in g.get('items', []):
                        Order.add_medicine(oid_new, int(it['medicine_id']), int(it['quantity']), float(it['unit_price']), float(it['subtotal']))
                        try:
                            if pid:
                                Database.execute('UPDATE inventory SET quantity = GREATEST(quantity - %s, 0) WHERE medicine_id=%s AND pharmacy_id=%s', (int(it['quantity']), int(it['medicine_id']), pid))
                            else:
                                Database.execute('UPDATE medicines SET quantity_in_stock = GREATEST(COALESCE(quantity_in_stock,0) - %s, 0) WHERE medicine_id=%s', (int(it['quantity']), int(it['medicine_id'])))
                        except Exception:
                            pass
                session.pop('pending_order', None)
                session.pop('cart', None)
                session['last_created_orders'] = created_orders
            except Exception as e:
                flash('Сталася помилка під час створення замовлення після оплати: ' + str(e), 'error')
                return redirect(url_for('cart.cart_view'))

        # оновлюємо статус замовлення на підтверджений
        try:
            if pending:
                for coid in session.get('last_created_orders', []):
                    Database.execute('UPDATE orders SET delivery_status=%s WHERE order_id=%s', ('confirmed', coid))
            else:
                Database.execute('UPDATE orders SET delivery_status=%s WHERE order_id=%s', ('confirmed', oid))
        except Exception:
            pass

        # Зберегти дані про оплату з ID замовлення для генерації чека
        if pending:
            created_oid = session.get('last_created_orders', [None])[0]
        else:
            created_oid = oid
        
        session['last_payment_order_id'] = created_oid
        session['last_payment_masked_card'] = masked_card
        session['last_payment_expiry'] = expiry_date

        flash('Оплата успішна! Замовлення підтверджено.', 'success')
        return redirect(url_for('orders.payment_success'))

    # визначити загальну суму для відображення
    if pending:
        try:
            total = float(sum(float(g.get('group_total', 0)) for g in pending.get('groups', [])))
        except Exception:
            total = 0.0
        return render_template('payment.html', pending=True, total=total)
    else:
        items = Order.get_items(oid)
        try:
            total = float(order.get('total_sum') or sum(float(item['subtotal']) for item in items))
        except Exception:
            total = sum(float(item['subtotal']) for item in items)

    return render_template('payment.html', order_id=oid, total=total, pending=False)

@bp.route('/payment/success')
def payment_success():
    return render_template('payment_success.html')

@bp.route('/download/payment_receipt')
def download_payment_receipt():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    # Отримати дані про останню оплату з сесії
    order_id = session.get('last_payment_order_id')
    masked_card = session.get('last_payment_masked_card')
    expiry_date = session.get('last_payment_expiry')
    
    # Якщо немає в сесії, спробувати отримати з payment_data
    if not order_id:
        payment_data = session.get('payment_data')
        if not payment_data:
            flash('Дані про оплату не знайдено', 'error')
            return redirect(url_for('main.index'))
        order_id = payment_data.get('order_id')
        masked_card = payment_data.get('masked_card')
        expiry_date = payment_data.get('expiry_date')
    
    if not order_id:
        flash('Дані про оплату не знайдено', 'error')
        return redirect(url_for('main.index'))
    
    order = Order.get_by_id(order_id)
    if not order or order['user_id'] != user['user_id']:
        flash('Замовлення не знайдено', 'error')
        return redirect(url_for('main.index'))
    
    items = Order.get_items(order['order_id'])
    total = float(order.get('total_sum', 0) or sum(float(item.get('subtotal', 0)) for item in items))
    
    pdf_buffer = generate_payment_receipt_pdf(order, items, user, masked_card or '****', expiry_date or '', total)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'payment_receipt_{order["order_id"]}.pdf'
    )

# завантаження PDF-файлу замовлення
@bp.route('/download_order/<int:oid>')
def download_order(oid):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    order = Order.get_by_id(oid)
    if not order or order['user_id'] != user['user_id']:
        # Додаткова спроба отримати order напряму з БД (можливо race condition після оформлення)
        order = Database.fetchone('SELECT * FROM orders WHERE order_id=%s', (oid,))
        if not order or order['user_id'] != user['user_id']:
            flash('Замовлення не знайдено', 'error')
            return redirect(url_for('main.index'))
    items = Order.get_items(order['order_id'])
    pdf_buffer = generate_order_pdf(order, items, user)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'order_{order["order_id"]}.pdf'
    )

@bp.route('/my_orders')
def my_orders():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.register', next='/my_orders'))
    
    update_order_statuses()
    orders = Order.get_by_user(user['user_id'])
    
    for order in orders:
        order['can_cancel'] = can_cancel_order_or_booking(order['order_date'], order['delivery_status'])
    
    return render_template('my_orders.html', orders=orders)

# скасування замовлення
@bp.route('/orders/delete/<int:oid>', methods=['POST'])
def order_delete(oid):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    order = Order.get_by_id(oid)
    if not order or order['user_id'] != user['user_id']:
        flash('Немає прав на цю дію', 'error')
        return redirect(url_for('profile.profile'))
    
    if not can_cancel_order_or_booking(order['order_date'], order['delivery_status']):
        flash('Замовлення вже неможливо скасувати!', 'error')
        return redirect(url_for('orders.my_orders'))
    
    Order.delete(oid)
    flash('Замовлення скасовано')
    return redirect(url_for('orders.my_orders'))


@bp.route('/internal/debug/order_data/<int:oid>')
def internal_debug_order_data(oid):
    # Отримати деталі замовлення для налагодження
    try:
        order = Database.fetchone('SELECT * FROM orders WHERE order_id=%s', (oid,))
        items = Database.fetchall('SELECT * FROM order_medicine WHERE order_id=%s', (oid,))
        return {
            'order': order,
            'items': items
        }
    except Exception as e:
        return {'error': str(e)}, 500