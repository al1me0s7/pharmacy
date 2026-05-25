from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models import Database, Statistics
from datetime import datetime, timedelta

bp = Blueprint('admin_dashboard', __name__, url_prefix='/admin')

# Переклад статусів на українську
def translate_status(status):
    translations = {
        'new': 'Нове',
        'pending': 'В очікуванні',
        'processing': 'Обробляється',
        'ready': 'Готово',
        'completed': 'Завершено',
        'delivered': 'Доставлено',
        'cancelled': 'Скасовано',
        'received': 'Отримано',
        'collected': 'ОТРИМАНО',
        'expired': 'Термін закінчився',
        'confirmed': 'Підтверджено',
        'declined': 'Відхилено',
        'shipped': 'Відправлено',
        'unknown': 'Невідомий'
    }
    return translations.get(status, status)

@bp.route('/')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_auth.admin_login'))
    
    # Статистика за останні 30 днів (за замовчуванням)
    date_from = (datetime.now() - timedelta(days=30)).date()
    date_to = datetime.now().date()
    
    stats = {
        # CRUD: Знайти - підрахунок користувачів
        'total_users': len(Database.fetchall('SELECT user_id FROM users')),
        'total_orders': Statistics.total_orders(),
        'total_bookings': Statistics.total_bookings(),
        # CRUD: Знайти - підрахунок загального доходу
        'total_revenue': Database.fetchone(
            'SELECT COALESCE(SUM(total_sum), 0) as total FROM orders'
        ).get('total', 0),
    }
    
    return render_template('admin/dashboard.html', stats=stats, date_from=date_from, date_to=date_to)

@bp.route('/stats')
def admin_stats():
    """Інтерактивна сторінка статистики з фільтрами по датах"""
    if not session.get('admin'):
        return redirect(url_for('admin_auth.admin_login'))
    
    # Отримати дати з параметрів запиту
    date_from_str = request.args.get('date_from')
    date_to_str = request.args.get('date_to')
    stat_type = request.args.get('type', 'orders')  # orders, bookings, revenue, medicines
    
    # Задати стандартні значення (останні 30 днів)
    if not date_from_str:
        date_from = (datetime.now() - timedelta(days=30)).date()
    else:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except:
            date_from = (datetime.now() - timedelta(days=30)).date()
    
    if not date_to_str:
        date_to = datetime.now().date()
    else:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except:
            date_to = datetime.now().date()
    
    stats_data = {}
    
    if stat_type == 'orders':
        # Статистика по замовленнях
        orders = Database.fetchall(
            'SELECT o.*, COUNT(om.medicine_id) as items_count FROM orders o LEFT JOIN order_medicine om ON o.order_id = om.order_id WHERE DATE(o.order_date) >= %s AND DATE(o.order_date) <= %s GROUP BY o.order_id ORDER BY o.order_date DESC',
            (date_from, date_to)
        )
        orders_enriched = []
        for o in orders:
            o_dict = dict(o)
            o_dict['delivery_status_translated'] = translate_status(o.get('delivery_status', 'unknown'))
            orders_enriched.append(o_dict)
        
        stats_data = {
            'total_orders': len(orders),
            'total_revenue': sum(float(o.get('total_sum', 0)) for o in orders),
            'avg_order': sum(float(o.get('total_sum', 0)) for o in orders) / len(orders) if orders else 0,
            'by_status': {},
            'orders_list': orders_enriched
        }
        for o in orders_enriched:
            status = o.get('delivery_status', 'unknown')
            translated_status = translate_status(status)
            if translated_status not in stats_data['by_status']:
                stats_data['by_status'][translated_status] = 0
            stats_data['by_status'][translated_status] += 1
    
    elif stat_type == 'bookings':
        # Статистика по бронюванням
        bookings = Database.fetchall(
            'SELECT * FROM bookings WHERE DATE(booking_date) >= %s AND DATE(booking_date) <= %s ORDER BY booking_date DESC',
            (date_from, date_to)
        )

        bookings_enriched = []
        for b in bookings:
            b_dict = dict(b)
            # Переводим статус
            b_dict['status_translated'] = translate_status(b.get('status', 'unknown'))
            if b.get('status') in ('collected', 'received'):
                try:
                    items = Database.fetchall(
                        'SELECT SUM(quantity * price_at_booking) as total_sum FROM booking_items WHERE booking_id = %s',
                        (b.get('booking_id'),)
                    )
                    if items and items[0].get('total_sum'):
                        b_dict['total_sum'] = float(items[0].get('total_sum', 0))
                    else:
                        b_dict['total_sum'] = 0
                except Exception:
                    b_dict['total_sum'] = 0
            else:
                b_dict['total_sum'] = 0
            bookings_enriched.append(b_dict)
        
        stats_data = {
            'total_bookings': len(bookings),
            'by_status': {},
            'bookings_list': bookings_enriched
        }
        for b in bookings_enriched:
            status = b.get('status', 'unknown')
            translated_status = translate_status(status)
            if translated_status not in stats_data['by_status']:
                stats_data['by_status'][translated_status] = 0
            stats_data['by_status'][translated_status] += 1
    
    elif stat_type == 'revenue':
        # Статистика по доходу
        orders = Database.fetchall(
            'SELECT * FROM orders WHERE DATE(order_date) >= %s AND DATE(order_date) <= %s ORDER BY order_date DESC',
            (date_from, date_to)
        )
        daily_revenue = {}
        for o in orders:
            order_date = str(o.get('order_date', '')).split()[0]
            if order_date not in daily_revenue:
                daily_revenue[order_date] = 0
            daily_revenue[order_date] += float(o.get('total_sum', 0))
        
        stats_data = {
            'total_revenue': sum(daily_revenue.values()),
            'daily_revenue': daily_revenue,
            'avg_daily': sum(daily_revenue.values()) / len(daily_revenue) if daily_revenue else 0
        }
    
    elif stat_type == 'medicines':
        # Статистика по найпопулярнішим ліками
        items = Database.fetchall(
            '''SELECT om.medicine_id, m.name, SUM(om.quantity) as total_sold, SUM(om.subtotal) as revenue
               FROM order_medicine om
               JOIN medicines m ON om.medicine_id = m.medicine_id
               JOIN orders o ON om.order_id = o.order_id
               WHERE DATE(o.order_date) >= %s AND DATE(o.order_date) <= %s
               GROUP BY om.medicine_id, m.name
               ORDER BY total_sold DESC
               LIMIT 20''',
            (date_from, date_to)
        )
        stats_data = {
            'top_medicines': items
        }
    
    return render_template('admin/statistics.html', 
                         stats=stats_data, 
                         stat_type=stat_type,
                         date_from=date_from,
                         date_to=date_to)

# PDF ЗВІТИ
@bp.route('/reports/sales', methods=['GET'])
def report_sales():
    """Звіт по продажах за період - PDF"""
    if not session.get('admin'):
        return redirect(url_for('admin_auth.admin_login'))
    
    date_from = request.args.get('date_from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        orders = Database.fetchall(
            'SELECT * FROM orders WHERE DATE(order_date) >= %s AND DATE(order_date) <= %s ORDER BY order_date DESC',
            (date_from, date_to)
        )
        total_revenue = sum(float(o.get('total_sum', 0)) for o in orders)
        
        from app.utils.pdf_generator import generate_sales_report_pdf
        pdf_buffer = generate_sales_report_pdf(date_from, date_to, orders, total_revenue)
        
        from flask import send_file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Звіт_продажів_{date_from}_{date_to}.pdf'
        )
    except Exception as e:
        flash(f'Помилка при генерації звіту: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard.admin_stats'))

@bp.route('/reports/medicines', methods=['GET'])
def report_medicines():
    """Звіт по популярних ліках - PDF"""
    if not session.get('admin'):
        return redirect(url_for('admin_auth.admin_login'))
    
    date_from = request.args.get('date_from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        items = Database.fetchall(
            '''SELECT om.medicine_id, m.name, SUM(om.quantity) as total_sold, SUM(om.subtotal) as revenue
               FROM order_medicine om
               JOIN medicines m ON om.medicine_id = m.medicine_id
               JOIN orders o ON om.order_id = o.order_id
               WHERE DATE(o.order_date) >= %s AND DATE(o.order_date) <= %s
               GROUP BY om.medicine_id, m.name
               ORDER BY total_sold DESC
               LIMIT 50''',
            (date_from, date_to)
        )
        
        from app.utils.pdf_reports import generate_medicines_report_pdf
        pdf_buffer = generate_medicines_report_pdf(date_from, date_to, items)
        
        from flask import send_file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Звіт_ліків_{date_from}_{date_to}.pdf'
        )
    except Exception as e:
        flash(f'Помилка при генерації звіту: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard.admin_stats'))

@bp.route('/reports/customer/<int:user_id>', methods=['GET'])
def report_customer(user_id):
    """Звіт по клієнту - його замовлення та бронювання - PDF"""
    if not session.get('admin'):
        return redirect(url_for('admin_auth.admin_login'))
    
    try:
        from app.models import User
        user = User.get_by_id(user_id)
        if not user:
            flash('Користувача не знайдено', 'error')
            return redirect(url_for('admin_dashboard.admin_stats'))
        
        orders = Database.fetchall('SELECT * FROM orders WHERE user_id=%s ORDER BY order_date DESC', (user_id,))
        bookings = Database.fetchall('SELECT * FROM bookings WHERE user_id=%s ORDER BY booking_date DESC', (user_id,))
        
        from app.utils.pdf_generator import generate_customer_report_pdf
        pdf_buffer = generate_customer_report_pdf(user, orders, bookings)
        
        from flask import send_file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Звіт_клієнта_{user_id}_{user.get("full_name", "unknown").replace(" ", "_")}.pdf'
        )
    except Exception as e:
        flash(f'Помилка при генерації звіту: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard.admin_stats'))
def admin_update_statuses():
    if not session.get('admin'):
        return redirect(url_for('admin_auth.admin_login'))
    try:
        from app.utils.helpers import update_order_statuses
        update_order_statuses()
        from app.models import Booking
        Booking.update_expired()
        flash('Статуси оновлені', 'success')
    except Exception as e:
        flash(f'Помилка при оновленні: {str(e)}', 'error')
    return redirect(url_for('admin_dashboard.admin_dashboard'))

@bp.route('/order/<int:order_id>/update_status', methods=['POST'])
def admin_order_update_status(order_id):
    if not session.get('admin'):
        return redirect(url_for('admin_auth.admin_login'))
    new_status = request.form.get('status')
    if not new_status:
        flash('✗ Вкажіть новий статус', 'error')
        return redirect(request.referrer or url_for('admin_orders.admin_orders'))
    try:
        # CRUD: Оновити - зміна статусу замовлення
        Database.execute('UPDATE orders SET delivery_status=%s, status_last_updated = CURRENT_TIMESTAMP WHERE order_id=%s', (new_status, order_id))
        flash('Статус замовлення оновлено', 'success')
    except Exception as e:
        flash(f'Помилка при оновленні статусу: {e}', 'error')
    return redirect(request.referrer or url_for('admin_orders.admin_orders'))

@bp.route('/booking/<int:booking_id>/update_status', methods=['POST'])
def admin_booking_update_status(booking_id):
    if not session.get('admin'):
        return redirect(url_for('admin_auth.admin_login'))
    new_status = request.form.get('status')
    if not new_status:
        flash('Вкажіть новий статус', 'error')
        return redirect(request.referrer or url_for('admin_bookings.admin_bookings'))
    try:
        Database.execute('UPDATE bookings SET status=%s, status_last_updated = CURRENT_TIMESTAMP WHERE booking_id=%s', (new_status, booking_id))
        flash('Статус бронювання оновлено', 'success')
    except Exception as e:
        flash(f'Помилка при оновленні статусу: {e}', 'error')
    return redirect(request.referrer or url_for('admin_bookings.admin_bookings'))

@bp.route('/export/orders')
def export_orders():
    """Експорт замовлень в PDF"""
    if not session.get('admin'):
        return redirect(url_for('admin_auth.admin_login'))
    
    date_from_str = request.args.get('date_from')
    date_to_str = request.args.get('date_to')
    
    if not date_from_str:
        date_from = (datetime.now() - timedelta(days=30)).date()
    else:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except:
            date_from = (datetime.now() - timedelta(days=30)).date()
    
    if not date_to_str:
        date_to = datetime.now().date()
    else:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except:
            date_to = datetime.now().date()
    
    from app.utils.pdf_reports import generate_sales_report_pdf
    from flask import send_file
    import io
    
    pdf = generate_sales_report_pdf(date_from, date_to)
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'Замовлення_{date_from}_{date_to}.pdf'
    )

@bp.route('/export/bookings')
def export_bookings():
    """Експорт бронювань в PDF"""
    if not session.get('admin'):
        return redirect(url_for('admin_auth.admin_login'))
    
    date_from_str = request.args.get('date_from')
    date_to_str = request.args.get('date_to')
    
    if not date_from_str:
        date_from = (datetime.now() - timedelta(days=30)).date()
    else:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except:
            date_from = (datetime.now() - timedelta(days=30)).date()
    
    if not date_to_str:
        date_to = datetime.now().date()
    else:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except:
            date_to = datetime.now().date()
    
    from app.utils.pdf_reports import generate_bookings_report_pdf
    from flask import send_file
    import io
    
    pdf = generate_bookings_report_pdf(date_from, date_to)
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'Бронювання_{date_from}_{date_to}.pdf'
    )

@bp.route('/export/revenue')
def export_revenue():
    """Експорт доходу в PDF"""
    if not session.get('admin'):
        return redirect(url_for('admin_auth.admin_login'))
    
    date_from_str = request.args.get('date_from')
    date_to_str = request.args.get('date_to')
    
    if not date_from_str:
        date_from = (datetime.now() - timedelta(days=30)).date()
    else:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except:
            date_from = (datetime.now() - timedelta(days=30)).date()
    
    if not date_to_str:
        date_to = datetime.now().date()
    else:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except:
            date_to = datetime.now().date()
    
    from app.utils.pdf_reports import generate_revenue_report_pdf
    from flask import send_file
    import io
    
    pdf = generate_revenue_report_pdf(date_from, date_to)
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'Дохід_{date_from}_{date_to}.pdf'
    )

@bp.route('/export/medicines')
def export_medicines():
    """Експорт популярних ліків в PDF"""
    if not session.get('admin'):
        return redirect(url_for('admin_auth.admin_login'))
    
    date_from_str = request.args.get('date_from')
    date_to_str = request.args.get('date_to')
    
    if not date_from_str:
        date_from = (datetime.now() - timedelta(days=30)).date()
    else:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except:
            date_from = (datetime.now() - timedelta(days=30)).date()
    
    if not date_to_str:
        date_to = datetime.now().date()
    else:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except:
            date_to = datetime.now().date()
    
    from app.utils.pdf_reports import generate_medicines_report_pdf
    from flask import send_file
    import io
    
    pdf = generate_medicines_report_pdf(date_from, date_to)
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'Популярні_ліки_{date_from}_{date_to}.pdf'
    )