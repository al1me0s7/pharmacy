from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils.helpers import get_current_user, update_order_statuses, translate_order_status
from app.models import User, Order, Booking, City

bp = Blueprint('profile', __name__)

# оновлення профілю користувача
@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.register', next='/profile'))
    
    if request.method == 'POST':
        User.update(
            user['user_id'],
            request.form.get('full_name'),
            None,
            request.form.get('phone'),
            request.form.get('address'),
            request.form.get('city'),
            request.form.get('postal_code')
        )
        flash('Профіль оновлено')
        return redirect(url_for('profile.profile'))
    
    user = User.find_by_id(user['user_id'])
    update_order_statuses()
    orders = Order.get_by_user(user['user_id'])
    bookings = Booking.get_by_user(user['user_id'])
    
    # Відображення статусів замовлень та бронювань
    status_map = {
        'pending': 'Очікує',
        'confirmed': 'Підтверджено',
        'shipped': 'Відправлено',
        'delivered': 'Доставлено',
        'cancelled': 'Скасовано',
        'active': 'Активне',
        'collected': 'Отримано',
        'expired': 'Закінчилось'
    }
    
    for order in orders:
        order['status_display'] = status_map.get(order.get('delivery_status'), order.get('delivery_status'))
        order['can_cancel'] = order.get('delivery_status') not in ['shipped', 'delivered']
    
    for booking in bookings:
        booking['status_display'] = status_map.get(booking.get('status'), booking.get('status'))
        booking['can_cancel'] = booking['status'] == 'active'
    
    cities = City.get_all()
    
    return render_template('profile.html', user=user, orders=orders, bookings=bookings, cities=cities)

@bp.route('/profile/delete', methods=['POST'])
def profile_delete():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    User.delete(user['user_id'])
    session.pop('user_id', None)
    session.pop('cart', None)
    flash('Ваш акаунт видалено')
    return redirect(url_for('main.index'))