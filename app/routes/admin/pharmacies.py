from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Database
from app.utils.decorators import admin_required

bp = Blueprint('admin_pharmacies', __name__, url_prefix='/admin')
# CRUD: Знайти - перегляд списку аптек
@bp.route('/pharmacies')
@admin_required
def admin_pharmacies():
    search = request.args.get('search', '').strip()
    
    sql = '''SELECT p.*, c.city_name FROM pharmacies p 
             LEFT JOIN cities c ON p.city_id = c.city_id 
             WHERE 1=1'''
    params = []
    
    if search:
        sql += " AND (p.pharmacy_name ILIKE %s OR p.address ILIKE %s OR p.contact_phone ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    
    sql += ' ORDER BY p.pharmacy_name ASC'
    
    # CRUD: Знайти - пошук аптек
    pharmacies = Database.fetchall(sql, tuple(params) if params else None)
    
    # Получить список городов для формы добавления
    cities = Database.fetchall('SELECT * FROM cities ORDER BY city_name')
    
    return render_template('admin/pharmacies.html', pharmacies=pharmacies, search=search, cities=cities)

@bp.route('/pharmacies/search')
@admin_required
def admin_pharmacies_search():
    search = request.args.get('search', '').strip()
    
    sql = '''SELECT p.*, c.city_name FROM pharmacies p 
             LEFT JOIN cities c ON p.city_id = c.city_id 
             WHERE 1=1'''
    params = []
    
    if search:
        sql += " AND (p.pharmacy_name ILIKE %s OR p.address ILIKE %s OR p.contact_phone ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    
    sql += ' ORDER BY p.pharmacy_name ASC'
    
    # CRUD: Знайти - пошук аптек
    pharmacies = Database.fetchall(sql, tuple(params) if params else None)
    return render_template('admin/partials/pharmacies_table.html', pharmacies=pharmacies)

@bp.route('/pharmacies/add', methods=['GET', 'POST'])
@admin_required
def admin_pharmacies_add():
    if request.method == 'POST':
        pharmacy_name = request.form.get('pharmacy_name', '').strip()
        city_id = request.form.get('city_id', '').strip()
        address = request.form.get('address', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        working_hours = request.form.get('working_hours', '').strip()
        email = request.form.get('email', '').strip()
        has_delivery = request.form.get('has_delivery') == 'on'
        
        if not pharmacy_name or not address or not city_id:
            flash('Назва аптеки, адреса та місто обов\'язкові', 'error')
            return redirect(url_for('admin_pharmacies.admin_pharmacies_add'))
        
        try:
            # CRUD: Створити - додавання аптеки
            Database.execute('''
                INSERT INTO pharmacies (pharmacy_name, city_id, address, contact_phone, working_hours, email, has_delivery)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (pharmacy_name, city_id, address, contact_phone, working_hours, email, has_delivery))
            flash('✓ Аптеку додано')
            return redirect(url_for('admin_pharmacies.admin_pharmacies'))
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')
    
    # список городов для формы
    cities = Database.fetchall('SELECT * FROM cities ORDER BY city_name')
    return render_template('admin/pharmacies_add.html', cities=cities)

@bp.route('/pharmacies/<int:pid>/edit', methods=['GET', 'POST'])
@admin_required
def admin_pharmacies_edit(pid):
    if request.method == 'POST':
        pharmacy_name = request.form.get('pharmacy_name', '').strip()
        city_id = request.form.get('city_id', '').strip()
        address = request.form.get('address', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        working_hours = request.form.get('working_hours', '').strip()
        email = request.form.get('email', '').strip()
        has_delivery = request.form.get('has_delivery') == 'on'
        
        if not pharmacy_name or not address or not city_id:
            flash('Назва аптеки, адреса та місто обов\'язкові', 'error')
            return redirect(url_for('admin_pharmacies.admin_pharmacies_edit', pid=pid))
        
        try:
            # CRUD: Оновити - редагування аптеки
            Database.execute('''
                UPDATE pharmacies SET pharmacy_name=%s, city_id=%s, address=%s, contact_phone=%s, working_hours=%s, email=%s, has_delivery=%s
                WHERE pharmacy_id=%s
            ''', (pharmacy_name, city_id, address, contact_phone, working_hours, email, has_delivery, pid))
            flash('Аптеку оновлено')
            return redirect(url_for('admin_pharmacies.admin_pharmacies'))
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')
    
    # CRUD: Знайти - отримання аптеки для редагування
    pharmacy = Database.fetchone('SELECT p.*, c.city_name FROM pharmacies p LEFT JOIN cities c ON p.city_id = c.city_id WHERE p.pharmacy_id=%s', (pid,))
    if not pharmacy:
        flash('Аптеку не знайдено', 'error')
        return redirect(url_for('admin_pharmacies.admin_pharmacies'))
    
    # Получить список городов для формы
    cities = Database.fetchall('SELECT * FROM cities ORDER BY city_name')
    return render_template('admin/pharmacies_edit.html', pharmacy=pharmacy, cities=cities)

@bp.route('/pharmacies/<int:pid>/delete', methods=['POST'])
@admin_required
def admin_pharmacies_delete(pid):
    try:
        # CRUD: Видалити - видалення аптеки
        Database.execute('DELETE FROM pharmacies WHERE pharmacy_id=%s', (pid,))
        flash('Аптеку видалено')
    except Exception as e:
        flash(f'Помилка: {str(e)}', 'error')
    return redirect(url_for('admin_pharmacies.admin_pharmacies'))