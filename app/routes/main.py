from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models import Medicine, Category, Manufacturer, City, Statistics, Database, Pharmacy
from app.utils.helpers import get_current_user

bp = Blueprint('main', __name__)
# CRUD: Відобразити - головна сторінка
@bp.route('/')
def index():
    q = request.args.get('q', '').strip()
    city_id = request.args.get('city_id')
    categories = request.args.getlist('categories')
    manufacturers = request.args.getlist('manufacturers')
    prescription = request.args.get('prescription', '')
    sort = request.args.get('sort', 'name')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    if city_id:
        session['selected_city_id'] = city_id
    
    meds = Medicine.search(query=q, category=categories[0] if categories else None, 
                          manufacturer=manufacturers[0] if manufacturers else None, 
                          prescription=prescription, sort=sort, city=city_id if city_id else None)
    
    if categories and len(categories) > 1:
        cat_ids = [int(c) for c in categories if c.isdigit()]
        if cat_ids:
            meds = [m for m in meds if m.get('category_id') in cat_ids]
    
    if manufacturers and len(manufacturers) > 1:
        mf_ids = [int(m) for m in manufacturers if m.isdigit()]
        if mf_ids:
            meds = [m for m in meds if m.get('manufacturer_id') in mf_ids]
    
    if min_price:
        try:
            min_p = float(min_price)
            meds = [m for m in meds if m.get('price', 0) >= min_p]
        except:
            pass
    if max_price:
        try:
            max_p = float(max_price)
            meds = [m for m in meds if m.get('price', 0) <= max_p]
        except:
            pass
    
    stats = {
        'total_orders': Statistics.total_orders(),
        'total_bookings': Statistics.total_bookings(),
        'avg_order': round(Statistics.average_order(), 2),
        'top_medicines': Statistics.top_medicines()
    }
    
    all_categories = Category.get_all()
    all_manufacturers = Manufacturer.get_all()
    cities = City.get_all()
    # CRUD: Відобразити - рендеринг головної сторінки з фільтрами
    return render_template(
        'index.html',
        meds=meds,
        categories=all_categories,
        manufacturers=all_manufacturers,
        cities=cities,
        q=q,
        city_id=city_id,
        categories_list=[str(c) for c in categories],
        manufacturers_list=[str(m) for m in manufacturers],
        prescription=prescription,
        sort=sort,
        stats=stats
    )
# CRUD: Знайти - пошук ліків з фільтрами
@bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    city_id = request.args.get('city_id')
    categories = request.args.getlist('categories')
    manufacturers = request.args.getlist('manufacturers')
    prescription = request.args.get('prescription', '')
    sort = request.args.get('sort', 'name')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    meds = Medicine.search(query=q, category=None, 
                          manufacturer=None, 
                          prescription=prescription, sort=sort, 
                          city=city_id if city_id else None)
    
    if categories:
        cat_ids = [int(c) for c in categories if c.isdigit()]
        if cat_ids:
            meds = [m for m in meds if m.get('category_id') in cat_ids]
    
    if manufacturers:
        mf_ids = [int(m) for m in manufacturers if m.isdigit()]
        if mf_ids:
            meds = [m for m in meds if m.get('manufacturer_id') in mf_ids]
    
    if min_price:
        try:
            min_p = float(min_price)
            meds = [m for m in meds if m.get('price', 0) >= min_p]
        except:
            pass
    if max_price:
        try:
            max_p = float(max_price)
            meds = [m for m in meds if m.get('price', 0) <= max_p]
        except:
            pass
    
    return render_template('partials/cards.html', meds=meds)
# CRUD: Відобразити - деталі ліків
@bp.route('/medicine/<int:mid>')
def medicine_detail(mid):
    med = Database.fetchone('''
        SELECT m.*, c.category_name, mf.manufacturer_name
        FROM medicines m
        LEFT JOIN categories c ON m.category_id = c.category_id
        LEFT JOIN manufacturers mf ON m.manufacturer_id = mf.manufacturer_id
        WHERE m.medicine_id = %s
    ''', (mid,))
    if not med:
        return 'Препарат не знайдено', 404

    pharmacies = Pharmacy.get_all()
    reviews = Database.fetchall(
        'SELECT r.*, u.full_name FROM reviews r JOIN users u ON r.user_id=u.user_id WHERE r.medicine_id=%s ORDER BY r.created_at DESC',
        (mid,)
    )
    return render_template('medicine.html', med=med, pharmacies=pharmacies, reviews=reviews)

@bp.route('/medicine/<int:mid>/prices')
def medicine_prices(mid):
    med = Medicine.get_by_id(mid)
    if not med:
        return 'Ліків не знайдено', 404
    
    city_id = request.args.get('city_id')
    
    query = '''
    SELECT 
        p.pharmacy_id,
        i.selling_price AS price,
        p.pharmacy_name,
        p.address,
        c.city_name,
        c.city_id,
        p.working_hours,
        p.contact_phone
    FROM pharmacies p
    LEFT JOIN inventory i 
        ON i.pharmacy_id = p.pharmacy_id AND i.medicine_id = %s
    JOIN cities c ON p.city_id = c.city_id
    WHERE i.selling_price IS NOT NULL
    '''
    
    params = [mid]

    if city_id:
        query += ' AND p.city_id = %s'
        params.append(city_id)

    query += ' ORDER BY price ASC'

    prices = Database.fetchall(query, tuple(params))

    cities = Database.fetchall('SELECT * FROM cities ORDER BY city_name')

    return render_template(
        'medicine_prices.html',
        med=med, prices=prices, cities=cities,
        selected_city_id=city_id
    )

# CRUD: Отримати ціни для кошика через api
@bp.route('/api/cart/prices')
def api_cart_prices():
    pharmacy_id = request.args.get('pharmacy_id')
    if not pharmacy_id:
        return jsonify({'error': 'No pharmacy_id'}), 400
    
    from app.utils.helpers import get_cart_items
    cart = session.get('cart', {})
    updated_cart = {}
    for key, qty in cart.items():
        if ':' not in key:
            updated_cart[f'{key}:{pharmacy_id}'] = qty
        else:
            updated_cart[key] = qty
    
    session['cart'] = updated_cart
    items, total = get_cart_items()
    session['cart'] = cart
    
    return jsonify({
        'items': [{'key': i['key'], 'unit_price': i['unit_price'], 'subtotal': i['subtotal']} for i in items],
        'total': total
    })
# CRUD: Створити - додавання відгуку для ліків
@bp.route('/medicine/<int:mid>/review', methods=['POST'])
def add_review(mid):
    user = get_current_user()
    if not user:
        flash('Увійдіть для додавання відгуку')
        return redirect(url_for('auth.login'))
    
    rating = request.form.get('rating')
    comment = request.form.get('comment', '').strip()
    
    if not rating or not (1 <= int(rating) <= 5):
        flash('Оберіть рейтинг від 1 до 5')
        return redirect(url_for('main.medicine_detail', mid=mid))
    
    # CRUD: Знайти - перевірка наявності відгуку
    existing = Database.fetchone('SELECT review_id FROM reviews WHERE medicine_id=%s AND user_id=%s', (mid, user['user_id']))
    if existing:
        flash('Ви вже залишили відгук')
        return redirect(url_for('main.medicine_detail', mid=mid))
    
    # CRUD: Створити - додавання відгуку
    Database.execute('INSERT INTO reviews (medicine_id, user_id, rating, comment) VALUES (%s, %s, %s, %s)', (mid, user['user_id'], int(rating), comment))
    flash('Відгук додано')
    return redirect(url_for('main.medicine_detail', mid=mid))

@bp.route('/api/price')
def api_price():
    mid = request.args.get('medicine_id')
    pid = request.args.get('pharmacy_id')
    try:
        mid = int(mid)
    except:
        return jsonify({'error': 'invalid_medicine_id'}), 400
    try:
        pid = int(pid) if pid not in (None, '', 'null') else None
    except:
        pid = None

    med = Medicine.get_by_id(mid)
    if not med:
        return jsonify({'error': 'not_found'}), 404

    unit_price = float(med.get('price', 0))
    if pid:
        # Отримання ціни з inventory
        price_row = Database.fetchone(
            'SELECT price FROM inventory WHERE medicine_id=%s AND pharmacy_id=%s',
            (mid, pid)
        )
        if price_row and price_row.get('price') is not None:
            try:
                unit_price = float(price_row.get('price'))
            except:
                pass

    return jsonify({'medicine_id': mid, 'pharmacy_id': pid, 'price': unit_price})