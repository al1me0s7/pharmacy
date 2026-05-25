from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Database, Category, Manufacturer, Medicine, City, Pharmacy
from app.utils.decorators import admin_required
import os
from werkzeug.utils import secure_filename

bp = Blueprint('admin_medicines', __name__, url_prefix='/admin')

@bp.route('/medicines')
@admin_required
def admin_medicines():
    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '')
    manufacturer_filter = request.args.get('manufacturer', '')
    sort = request.args.get('sort', 'name')
    # CRUD: Знайти - перегляд списку ліків
    sql = '''SELECT m.*, c.category_name, mf.manufacturer_name,
             (SELECT COUNT(DISTINCT i.pharmacy_id) FROM inventory i WHERE i.medicine_id = m.medicine_id) as pharmacy_count
             FROM medicines m 
             LEFT JOIN categories c ON m.category_id=c.category_id 
             LEFT JOIN manufacturers mf ON m.manufacturer_id=mf.manufacturer_id WHERE 1=1'''
    params = []
    
    if search:
        sql += " AND (m.name ILIKE %s OR mf.manufacturer_name ILIKE %s OR m.active_substance ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    
    if category_filter:
        sql += " AND m.category_id = %s"
        params.append(category_filter)
    
    if manufacturer_filter:
        sql += " AND m.manufacturer_id = %s"
        params.append(manufacturer_filter)
    
    if search:
        sql += ' ORDER BY CASE WHEN LOWER(m.name) LIKE LOWER(%s) THEN 0 ELSE 1 END, m.name'
        params.append(f'{search}%')
    elif sort == 'price_asc':
        sql += ' ORDER BY m.price ASC'
    elif sort == 'price_desc':
        sql += ' ORDER BY m.price DESC'
    elif sort == 'date_new':
        sql += ' ORDER BY m.date_added DESC'
    elif sort == 'date_old':
        sql += ' ORDER BY m.date_added ASC'
    else:
        sql += ' ORDER BY m.name'
    
    # CRUD: Знайти - пошук ліків з фільтрами
    medicines = Database.fetchall(sql, tuple(params) if params else None)
    
    categories = Category.get_all()
    manufacturers = Manufacturer.get_all()
    
    return render_template('admin/medicines.html', 
                         medicines=medicines, 
                         categories=categories, 
                         manufacturers=manufacturers,
                         search=search,
                         category_filter=category_filter,
                         manufacturer_filter=manufacturer_filter,
                         sort=sort)

@bp.route('/medicines/search')
@admin_required
def admin_medicines_search():
    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '')
    manufacturer_filter = request.args.get('manufacturer', '')
    sort = request.args.get('sort', 'name')

    sql = '''SELECT m.*, c.category_name, mf.manufacturer_name,
             (SELECT COUNT(DISTINCT i.pharmacy_id) FROM inventory i WHERE i.medicine_id = m.medicine_id) as pharmacy_count
             FROM medicines m 
             LEFT JOIN categories c ON m.category_id=c.category_id 
             LEFT JOIN manufacturers mf ON m.manufacturer_id=mf.manufacturer_id WHERE 1=1'''
    params = []
    
    if search:
        sql += " AND (m.name ILIKE %s OR mf.manufacturer_name ILIKE %s OR m.active_substance ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    
    if category_filter:
        sql += " AND m.category_id = %s"
        params.append(category_filter)
    
    if manufacturer_filter:
        sql += " AND m.manufacturer_id = %s"
        params.append(manufacturer_filter)
    
    if search:
        sql += ' ORDER BY CASE WHEN LOWER(m.name) LIKE LOWER(%s) THEN 0 ELSE 1 END, m.name'
        params.append(f'{search}%')
    elif sort == 'price_asc':
        sql += ' ORDER BY m.price ASC'
    elif sort == 'price_desc':
        sql += ' ORDER BY m.price DESC'
    elif sort == 'date_new':
        sql += ' ORDER BY m.date_added DESC'
    elif sort == 'date_old':
        sql += ' ORDER BY m.date_added ASC'
    else:
        sql += ' ORDER BY m.name'
    
    # CRUD: Знайти - пошук ліків з фільтрами
    medicines = Database.fetchall(sql, tuple(params) if params else None)
    
    return render_template('admin/partials/medicines_table.html', medicines=medicines)

@bp.route('/medicines/add', methods=['GET', 'POST'])
@admin_required
def admin_medicines_add():
    if request.method == 'POST':
        try:
            image_filename = None
            if 'image' in request.files and request.files['image'].filename:
                file = request.files['image']
                filename = secure_filename(f"med_{int(__import__('datetime').datetime.now().timestamp())}_{file.filename}")
                file.save(os.path.join('static/medicines', filename))
                image_filename = f'/static/medicines/{filename}'
            
            # CRUD: Створити - додавання нового препарату
            mid = Database.execute(
                '''INSERT INTO medicines (name, description, active_substance, dosage_form, dosage_value, 
                   price, quantity_in_stock, expiration_date, manufacturer_id, category_id, prescription_required, contraindications, 
                   composition, usage_instructions, storage_conditions, image)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING medicine_id''',
                (request.form.get('name'), request.form.get('description'), 
                 request.form.get('active_substance'), request.form.get('dosage_form'),
                 request.form.get('dosage_value'), float(request.form.get('price', 0)),
                 int(request.form.get('quantity_in_stock', 0)), request.form.get('expiration_date') or None,
                 request.form.get('manufacturer_id') or None, request.form.get('category_id') or None,
                 request.form.get('prescription_required') == 'on',
                 request.form.get('contraindications'), request.form.get('composition'),
                 request.form.get('usage_instructions'), request.form.get('storage_conditions'),
                 image_filename),
                returning=True
            )
            
            # Додаємо в inventory для кожної аптеки
            pharmacy_ids = request.form.getlist('pharmacy_ids[]')
            inventory_prices = request.form.getlist('inventory_prices[]')
            medicine_price = float(request.form.get('price', 0))
            if pharmacy_ids:
                for pid, price in zip(pharmacy_ids, inventory_prices):
                    if pid:
                        final_price = float(price) if price else medicine_price
                        Database.execute(
                            'INSERT INTO inventory (medicine_id, pharmacy_id, selling_price) VALUES (%s, %s, %s) ON CONFLICT (medicine_id, pharmacy_id) DO UPDATE SET selling_price=EXCLUDED.selling_price',
                            (mid, int(pid), final_price)
                        )
            else:
                all_pharmacies = Database.fetchall('SELECT pharmacy_id FROM pharmacies')
                for ph in all_pharmacies:
                    Database.execute(
                        'INSERT INTO inventory (medicine_id, pharmacy_id, selling_price) VALUES (%s, %s, %s) ON CONFLICT (medicine_id, pharmacy_id) DO UPDATE SET selling_price=EXCLUDED.selling_price',
                        (mid, ph['pharmacy_id'], medicine_price)
                    )
            
            flash('Препарат успішно додано!', 'success')
            return redirect(url_for('admin_medicines.admin_medicines'))
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')
    
    categories = Category.get_all()
    manufacturers = Manufacturer.get_all()
    cities = City.get_all()
    pharmacies = Pharmacy.get_all()
    
    return render_template('admin/add_medicine.html', categories=categories, manufacturers=manufacturers, cities=cities, pharmacies=pharmacies)

@bp.route('/medicines/<int:mid>/edit', methods=['GET', 'POST'])
@admin_required
def admin_medicines_edit(mid):
    med = Medicine.get_by_id(mid)
    if not med:
        flash('Препарат не знайдено', 'error')
        return redirect(url_for('admin_medicines.admin_medicines'))
    
    if request.method == 'POST':
        try:
            image_filename = med.get('image')
            if 'image' in request.files and request.files['image'].filename:
                file = request.files['image']
                filename = secure_filename(f"med_{int(__import__('datetime').datetime.now().timestamp())}_{file.filename}")
                file.save(os.path.join('static/medicines', filename))
                image_filename = f'/static/medicines/{filename}'
            
            # CRUD: Оновити - редагування ліку
            Database.execute(
                '''UPDATE medicines SET name=%s, description=%s, active_substance=%s, 
                   dosage_form=%s, dosage_value=%s, price=%s, quantity_in_stock=%s, expiration_date=%s,
                   manufacturer_id=%s, category_id=%s, prescription_required=%s, contraindications=%s, 
                   composition=%s, usage_instructions=%s, storage_conditions=%s, image=%s 
                   WHERE medicine_id=%s''',
                (request.form.get('name'), request.form.get('description'),
                 request.form.get('active_substance'), request.form.get('dosage_form'),
                 request.form.get('dosage_value'), float(request.form.get('price', 0)),
                 int(request.form.get('quantity_in_stock', 0)), request.form.get('expiration_date') or None,
                 request.form.get('manufacturer_id') or None, request.form.get('category_id') or None,
                 request.form.get('prescription_required') == 'on',
                 request.form.get('contraindications'), request.form.get('composition'),
                 request.form.get('usage_instructions'), request.form.get('storage_conditions'),
                 image_filename, mid)
            )
            
            # Оновлення цін у inventory
            pharmacy_ids = request.form.getlist('pharmacy_ids[]')
            inventory_prices = request.form.getlist('inventory_prices[]')
            medicine_price = float(request.form.get('price', 0))
            if pharmacy_ids:
                for pid, price in zip(pharmacy_ids, inventory_prices):
                    if pid:
                        final_price = float(price) if price else medicine_price
                        Database.execute(
                            'INSERT INTO inventory (medicine_id, pharmacy_id, selling_price) VALUES (%s, %s, %s) ON CONFLICT (medicine_id, pharmacy_id) DO UPDATE SET selling_price=EXCLUDED.selling_price',
                            (mid, int(pid), final_price)
                        )
            
            flash('Препарат успішно оновлено!', 'success')
            return redirect(url_for('admin_medicines.admin_medicines'))
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')
    
    categories = Category.get_all()
    manufacturers = Manufacturer.get_all()
    cities = City.get_all()
    pharmacies = Pharmacy.get_all()
    
    # CRUD: Знайти - отримання існуючих цін для препарату
    existing_prices = Database.fetchall('''
        SELECT i.pharmacy_id, i.selling_price as price, p.pharmacy_name, c.city_name, p.city_id
        FROM inventory i
        JOIN pharmacies p ON i.pharmacy_id = p.pharmacy_id
        JOIN cities c ON p.city_id = c.city_id
        WHERE i.medicine_id = %s
    ''', (mid,))
    
    return render_template('admin/edit_medicine.html', med=med, categories=categories, manufacturers=manufacturers, cities=cities, pharmacies=pharmacies, existing_prices=existing_prices)

@bp.route('/medicines/<int:mid>/delete', methods=['POST'])
@admin_required
def admin_medicines_delete(mid):
    med = Medicine.get_by_id(mid)
    if not med:
        flash('Лік не знайдено', 'error')
        return redirect(url_for('admin_medicines.admin_medicines'))
    
    try:
        # CRUD: Видалити - видалення препарату
        Database.execute('DELETE FROM medicines WHERE medicine_id=%s', (mid,))
        flash('Препарат видалено', 'success')
    except Exception as e:
        if 'FOREIGN KEY' in str(e) or 'foreign key' in str(e):
            flash('Не можна видалити препарат, бо на нього посилаються замовлення або бронювання', 'error')
        else:
            flash(f'Помилка: {str(e)}', 'error')
    
    return redirect(url_for('admin_medicines.admin_medicines'))