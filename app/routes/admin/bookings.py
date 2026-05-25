from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Database
from app.utils.decorators import admin_required

bp = Blueprint('admin_bookings', __name__, url_prefix='/admin')

@bp.route('/bookings')
@admin_required
def admin_bookings():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')
    sort = request.args.get('sort', 'recent')

    # Основний SQL - беремо назву ліків з таблиці medicines
    sql = '''
        SELECT b.*, u.full_name, u.email, u.phone_number,
               p.pharmacy_name, p.address as pharmacy_address,
               m.name AS medicine_name
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN pharmacies p ON b.pharmacy_id = p.pharmacy_id
        JOIN medicines m ON b.medicine_id = m.medicine_id
        WHERE 1=1
    '''
    params = []

    # Пошук
    if search:
        sql += " AND (u.full_name ILIKE %s OR u.email ILIKE %s OR p.pharmacy_name ILIKE %s OR m.name ILIKE %s OR b.booking_id::text ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'])

    # Фільтр статусу
    if status_filter != 'all' and status_filter != '':
        sql += " AND b.status = %s"
        params.append(status_filter)

    # Сортування
    if sort == 'user':
        sql += ' ORDER BY u.full_name ASC'
    elif sort == 'pharmacy':
        sql += ' ORDER BY p.pharmacy_name ASC'
    elif sort == 'medicine':
        sql += ' ORDER BY m.name ASC'
    elif sort == 'oldest':
        sql += ' ORDER BY b.booking_date ASC'
    else:  # recent
        sql += ' ORDER BY b.booking_date DESC'

    bookings = Database.fetchall(sql, tuple(params) if params else None)
    return render_template('admin/bookings.html', bookings=bookings, search=search, status_filter=status_filter, sort=sort)


@bp.route('/bookings/search')
@admin_required
def admin_bookings_search():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')
    sort = request.args.get('sort', 'recent')

    sql = '''
        SELECT b.*, u.full_name, u.email, u.phone_number,
               p.pharmacy_name, p.address as pharmacy_address,
               m.name AS medicine_name
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN pharmacies p ON b.pharmacy_id = p.pharmacy_id
        JOIN medicines m ON b.medicine_id = m.medicine_id
        WHERE 1=1
    '''
    params = []

    if search:
        sql += " AND (u.full_name ILIKE %s OR u.email ILIKE %s OR p.pharmacy_name ILIKE %s OR m.name ILIKE %s OR b.booking_id::text ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'])

    if status_filter != 'all' and status_filter != '':
        sql += " AND b.status = %s"
        params.append(status_filter)

    if sort == 'user':
        sql += ' ORDER BY u.full_name ASC'
    elif sort == 'pharmacy':
        sql += ' ORDER BY p.pharmacy_name ASC'
    elif sort == 'medicine':
        sql += ' ORDER BY m.name ASC'
    elif sort == 'oldest':
        sql += ' ORDER BY b.booking_date ASC'
    else:
        sql += ' ORDER BY b.booking_date DESC'

    bookings = Database.fetchall(sql, tuple(params) if params else None)
    return render_template('admin/partials/bookings_table.html', bookings=bookings)


@bp.route('/bookings/<int:bid>')
@admin_required
def admin_booking_detail(bid):
    booking = Database.fetchone('''
        SELECT b.*, u.full_name, u.email, u.phone_number, u.address,
               p.pharmacy_name, p.address as pharmacy_address, p.phone_number as pharmacy_phone,
               m.name AS medicine_name, m.price AS medicine_price
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN pharmacies p ON b.pharmacy_id = p.pharmacy_id
        JOIN medicines m ON b.medicine_id = m.medicine_id
        WHERE b.booking_id = %s
    ''', (bid,))

    if not booking:
        flash('Бронювання не знайдено', 'error')
        return redirect(url_for('admin_bookings.admin_bookings'))

    return render_template('admin/booking_detail.html', booking=booking)


@bp.route('/bookings/<int:bid>/status', methods=['POST'])
@admin_required
def admin_booking_status(bid):
    new_status = request.form.get('status')
    valid_statuses = ['active', 'collected', 'expired', 'cancelled']

    if new_status not in valid_statuses:
        flash('Невірний статус', 'error')
        return redirect(url_for('admin_bookings.admin_booking_detail', bid=bid))

    try:
        Database.execute('UPDATE bookings SET status=%s, status_last_updated=NOW() WHERE booking_id=%s', (new_status, bid))
        flash('Статус бронювання оновлено')
    except Exception as e:
        flash(f'Помилка: {str(e)}', 'error')

    return redirect(url_for('admin_bookings.admin_booking_detail', bid=bid))
