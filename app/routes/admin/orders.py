from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Database
from app.utils.decorators import admin_required

bp = Blueprint('admin_orders', __name__, url_prefix='/admin')

@bp.route('/orders')
@admin_required
def admin_orders():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    sort = request.args.get('sort', 'recent')

    sql = '''
        SELECT o.*, u.full_name, u.email, u.phone_number,
               COUNT(om.medicine_id) AS items_count,
               COALESCE(SUM(om.quantity * om.price_at_purchase), 0) AS total_amount
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        LEFT JOIN order_medicine om ON o.order_id = om.order_id
        WHERE 1=1
    '''
    params = []

    # Пошук
    if search:
        sql += " AND (u.full_name ILIKE %s OR u.email ILIKE %s OR o.order_id::text ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

    # Фільтр статусу
    if status_filter:
        sql += " AND o.status = %s"
        params.append(status_filter)

    # GROUP BY для агрегацій
    sql += ' GROUP BY o.order_id, u.user_id, u.full_name, u.email, u.phone_number'

    # Сортування
    if sort == 'expensive':
        sql += ' ORDER BY total_amount DESC'
    elif sort == 'cheapest':
        sql += ' ORDER BY total_amount ASC'
    elif sort == 'user':
        sql += ' ORDER BY u.full_name ASC'
    elif sort == 'oldest':
        sql += ' ORDER BY o.order_date ASC'
    else:
        sql += ' ORDER BY o.order_date DESC'

    orders = Database.fetchall(sql, tuple(params) if params else None)
    return render_template('admin/orders.html', orders=orders, search=search, sort=sort, status_filter=status_filter)

@bp.route('/orders/search')
@admin_required
def admin_orders_search():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    sort = request.args.get('sort', 'recent')

    sql = '''
        SELECT o.*, u.full_name, u.email, u.phone_number,
               COUNT(om.medicine_id) AS items_count,
               COALESCE(SUM(om.quantity * om.price_at_purchase), 0) AS total_amount
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        LEFT JOIN order_medicine om ON o.order_id = om.order_id
        WHERE 1=1
    '''
    params = []

    if search:
        sql += " AND (u.full_name ILIKE %s OR u.email ILIKE %s OR o.order_id::text ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

    if status_filter:
        sql += " AND o.status = %s"
        params.append(status_filter)

    sql += ' GROUP BY o.order_id, u.user_id, u.full_name, u.email, u.phone_number'

    if sort == 'expensive':
        sql += ' ORDER BY total_amount DESC'
    elif sort == 'cheapest':
        sql += ' ORDER BY total_amount ASC'
    elif sort == 'user':
        sql += ' ORDER BY u.full_name ASC'
    elif sort == 'oldest':
        sql += ' ORDER BY o.order_date ASC'
    else:
        sql += ' ORDER BY o.order_date DESC'

    orders = Database.fetchall(sql, tuple(params) if params else None)
    return render_template('admin/partials/orders_table.html', orders=orders)
