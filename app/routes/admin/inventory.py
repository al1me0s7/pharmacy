from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Database
from app.utils.decorators import admin_required

bp = Blueprint('admin_inventory', __name__, url_prefix='/admin')

@bp.route('/inventory')
@admin_required
def admin_inventory():
    search = request.args.get('search', '').strip()
    pharmacy_filter = request.args.get('pharmacy', 'all')
    sort = request.args.get('sort', 'medicine')
    # CRUD: Знайти - перегляд списку наявностей
    sql = '''
        SELECT i.*, m.name as medicine_name, m.description, m.price,
               p.pharmacy_name, c.category_name, mf.manufacturer_name
        FROM inventory i
        JOIN medicines m ON i.medicine_id = m.medicine_id
        JOIN pharmacies p ON i.pharmacy_id = p.pharmacy_id
        LEFT JOIN categories c ON m.category_id = c.category_id
        LEFT JOIN manufacturers mf ON m.manufacturer_id = mf.manufacturer_id
        WHERE 1=1
    '''
    params = []
    
    if search:
        sql += " AND (m.medicine_name ILIKE %s OR p.pharmacy_name ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    if pharmacy_filter != 'all':
        sql += " AND pi.pharmacy_id = %s"
        params.append(pharmacy_filter)
    
    if sort == 'quantity':
        sql += ' ORDER BY pi.quantity DESC'
    elif sort == 'pharmacy':
        sql += ' ORDER BY p.pharmacy_name ASC'
    else:
        sql += ' ORDER BY m.medicine_name ASC'
    
    # CRUD: Знайти - пошук наявності з фільтрами
    inventory = Database.fetchall(sql, tuple(params) if params else None)
    
    # CRUD: Знайти - отримання списку аптек для фільтра
    pharmacies = Database.fetchall('SELECT pharmacy_id, pharmacy_name FROM pharmacies ORDER BY pharmacy_name ASC')
    
    return render_template('admin/inventory.html', inventory=inventory, pharmacies=pharmacies, 
                         search=search, pharmacy_filter=pharmacy_filter, sort=sort)

@bp.route('/inventory/search')
@admin_required
def admin_inventory_search():
    search = request.args.get('search', '').strip()
    pharmacy_filter = request.args.get('pharmacy', 'all')
    sort = request.args.get('sort', 'medicine')
    
    sql = '''
        SELECT i.*, m.name as medicine_name, m.description, m.price,
               p.pharmacy_name, c.category_name, mf.manufacturer_name
        FROM inventory i
        JOIN medicines m ON i.medicine_id = m.medicine_id
        JOIN pharmacies p ON i.pharmacy_id = p.pharmacy_id
        LEFT JOIN categories c ON m.category_id = c.category_id
        LEFT JOIN manufacturers mf ON m.manufacturer_id = mf.manufacturer_id
        WHERE 1=1
    '''
    params = []
    
    if search:
        sql += " AND (m.medicine_name ILIKE %s OR p.pharmacy_name ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    if pharmacy_filter != 'all':
        sql += " AND pi.pharmacy_id = %s"
        params.append(pharmacy_filter)
    
    if sort == 'quantity':
        sql += ' ORDER BY pi.quantity DESC'
    elif sort == 'pharmacy':
        sql += ' ORDER BY p.pharmacy_name ASC'
    else:
        sql += ' ORDER BY m.medicine_name ASC'
    
    # CRUD: Знайти - пошук інвентарю з фільтрами
    inventory = Database.fetchall(sql, tuple(params) if params else None)
    return render_template('admin/partials/inventory_table.html', inventory=inventory)

@bp.route('/inventory/<int:pid>/<int:mid>/update', methods=['POST'])
@admin_required
def admin_inventory_update(pid, mid):
    quantity = request.form.get('quantity', type=int)
    
    if quantity is None or quantity < 0:
        flash('Кількість повинна бути невід\'ємним числом', 'error')
        return redirect(url_for('admin_inventory.admin_inventory'))
    
    try:
        # CRUD: Оновити - оновлення кількості товару в інвентарі
        Database.execute('''
            UPDATE inventory SET quantity=%s, last_updated=NOW()
            WHERE pharmacy_id=%s AND medicine_id=%s
        ''', (quantity, pid, mid))
        flash('Кількість оновлено')
    except Exception as e:
        flash(f'Помилка: {str(e)}', 'error')
    
    return redirect(url_for('admin_inventory.admin_inventory'))

@bp.route('/inventory/add', methods=['GET', 'POST'])
@admin_required
def admin_inventory_add():
    if request.method == 'POST':
        pharmacy_id = request.form.get('pharmacy_id', type=int)
        medicine_id = request.form.get('medicine_id', type=int)
        quantity = request.form.get('quantity', type=int)
        
        if not pharmacy_id or not medicine_id or quantity is None or quantity < 0:
            flash('Всі поля обов\'язкові та кількість повинна бути невід\'ємною', 'error')
            return redirect(url_for('admin_inventory.admin_inventory_add'))
        
        try:
            # CRUD: Створити - додавання товару до інвентарю
            Database.execute('''
                INSERT INTO inventory (pharmacy_id, medicine_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (pharmacy_id, medicine_id) DO UPDATE SET
                quantity = inventory.quantity + EXCLUDED.quantity,
                last_updated = NOW()
            ''', (pharmacy_id, medicine_id, quantity))
            flash('Товар додано до інвентарю')
            return redirect(url_for('admin_inventory.admin_inventory'))
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')
    
    # CRUD: Знайти - отримання списку аптек для форми
    pharmacies = Database.fetchall('SELECT pharmacy_id, pharmacy_name FROM pharmacies ORDER BY pharmacy_name ASC')
    # CRUD: Знайти - отримання списку ліків для форми
    medicines = Database.fetchall('SELECT medicine_id, medicine_name FROM medicines ORDER BY medicine_name ASC')
    
    return render_template('admin/inventory_add.html', pharmacies=pharmacies, medicines=medicines)