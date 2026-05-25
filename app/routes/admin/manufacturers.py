from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Database
from app.utils.decorators import admin_required
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify

bp = Blueprint('admin_manufacturers', __name__, url_prefix='/admin')

@bp.route('/manufacturers')
@admin_required
def admin_manufacturers():
    search = request.args.get('search', '').strip()
    
    sql = 'SELECT * FROM manufacturers WHERE 1=1'
    params = []
    
    if search:
        sql += " AND manufacturer_name ILIKE %s"
        params.append(f'%{search}%')
    
    sql += ' ORDER BY manufacturer_name ASC'
    
    # CRUD: Знайти - пошук виробників
    manufacturers = Database.fetchall(sql, tuple(params) if params else None)
    return render_template('admin/manufacturers.html', manufacturers=manufacturers, search=search)

@bp.route('/manufacturers/search')
@admin_required
def admin_manufacturers_search():
    search = request.args.get('search', '').strip()
    
    sql = 'SELECT * FROM manufacturers WHERE 1=1'
    params = []
    
    if search:
        sql += " AND manufacturer_name ILIKE %s"
        params.append(f'%{search}%')
    
    sql += ' ORDER BY manufacturer_name ASC'
    
    # CRUD: Знайти - пошук виробників
    manufacturers = Database.fetchall(sql, tuple(params) if params else None)
    return render_template('admin/partials/manufacturers_table.html', manufacturers=manufacturers)

@bp.route('/manufacturers/add', methods=['GET', 'POST'])
@admin_required
def admin_manufacturers_add():
    if request.method == 'POST':
        manufacturer_name = request.form.get('manufacturer_name', '').strip()
        
        if not manufacturer_name:
            flash('Назва виробника обов\'язкова', 'error')
            return redirect(url_for('admin_manufacturers.admin_manufacturers_add'))
        
        try:
            # CRUD: Створити - додавання виробника
            Database.execute('INSERT INTO manufacturers (manufacturer_name) VALUES (%s)', (manufacturer_name,))
            flash('Виробника додано')
            return redirect(url_for('admin_manufacturers.admin_manufacturers'))
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')
    
    return render_template('admin/manufacturers_add.html')

@bp.route('/manufacturers/<int:mid>/edit', methods=['GET', 'POST'])
@admin_required
def admin_manufacturers_edit(mid):
    if request.method == 'POST':
        manufacturer_name = request.form.get('manufacturer_name', '').strip()
        country = request.form.get('country', '').strip()
        city = request.form.get('city', '').strip()
        address = request.form.get('address', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        license_number = request.form.get('license_number', '').strip()
        founded_year = request.form.get('founded_year', '').strip()

        if not manufacturer_name:
            flash('Назва виробника обов\'язкова', 'error')
            return redirect(url_for('admin_manufacturers.admin_manufacturers_edit', mid=mid))

        try:
            Database.execute('''
                UPDATE manufacturers
                SET manufacturer_name=%s,
                    country=%s,
                    city=%s,
                    address=%s,
                    contact_email=%s,
                    contact_phone=%s,
                    license_number=%s,
                    founded_year=%s
                WHERE manufacturer_id=%s
            ''', (manufacturer_name, country, city, address, contact_email, contact_phone, license_number, 
                  int(founded_year) if founded_year.isdigit() else None, mid))
            flash('Виробника оновлено')
            return redirect(url_for('admin_manufacturers.admin_manufacturers'))
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')

    # Отримуємо виробника для заповнення форми
    manufacturer = Database.fetchone('SELECT * FROM manufacturers WHERE manufacturer_id=%s', (mid,))
    if not manufacturer:
        flash('Виробника не знайдено', 'error')
        return redirect(url_for('admin_manufacturers.admin_manufacturers'))

    return render_template('admin/manufacturers_edit.html', manufacturer=manufacturer)

@bp.route('/manufacturers/<int:mid>/delete', methods=['POST'])
@admin_required
def admin_manufacturers_delete(mid):
    try:
        # CRUD: Видалити - видалення виробника
        Database.execute('DELETE FROM manufacturers WHERE manufacturer_id=%s', (mid,))
        flash('Виробника видалено')
    except Exception as e:
        flash(f'Помилка: {str(e)}', 'error')
    return redirect(url_for('admin_manufacturers.admin_manufacturers'))

@bp.route('/manufacturers/<int:mid>/check_medicines')
@admin_required
def check_medicines(mid):
    # Перевіряємо, чи є ліки, пов'язані з цим виробником
    row = Database.fetchone(
        "SELECT 1 FROM medicines WHERE manufacturer_id = %s LIMIT 1",
        (mid,)
    )
    return jsonify({'has_medicines': bool(row)})