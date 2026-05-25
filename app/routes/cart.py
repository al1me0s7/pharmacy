from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.utils.helpers import get_current_user, get_cart_items
from app.models import Medicine, Database

bp = Blueprint('cart', __name__)

# CRUD: Перегляд кошика
@bp.route('/cart')
def cart_view():
    items, total = get_cart_items()
    return render_template('cart.html', items=items, total=total)

@bp.route('/cart/add', methods=['POST'])
def cart_add():
    mid = request.form.get('medicine_id') or request.args.get('medicine_id')
    qty = int(request.form.get('quantity', 1))
    
    if not mid:
        return redirect(url_for('main.index'))
    
    med = Medicine.get_by_id(mid)
    if not med:
        flash('Препарат не знайдено', 'error')
        return redirect(request.referrer or url_for('main.index'))

    pharmacy_id = request.form.get('pharmacy') or request.args.get('pharmacy')
    if pharmacy_id in ('', None):
        pharmacy_id = None
    else:
        try:
            pharmacy_id = int(pharmacy_id)
        except:
            pharmacy_id = None

    cart = session.get('cart', {})
    key = f"{int(mid)}:{pharmacy_id or ''}"
    existing = cart.get(key, 0)
    try:
        existing = int(existing) if not isinstance(existing, dict) else int(existing.get('quantity', 0))
    except:
        existing = 0
    cart[key] = existing + qty
    session['cart'] = cart
    
    if request.headers.get('Accept') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        items, total = get_cart_items()
        return jsonify({
            'cart_count': len(session.get('cart', {})),
            'items': [{'name': i['medicine'].get('name'), 'qty': i['quantity'], 'price': float(i.get('unit_price', i['medicine'].get('price', 0))), 'pharmacy_id': i.get('pharmacy_id')} for i in items],
            'total': total
        })
    
    flash(f'✓ "{med.get("name")}" додано до кошика!', 'success')
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/cart/update', methods=['POST'])
def cart_update():
    cart = session.get('cart', {})
    
    if request.is_json:
        data = request.get_json()
        items = data.get('items', [])
        cart = {}
        for item in items:
            key = item.get('key')
            qty = item.get('qty', 0)
            if qty > 0:
                cart[key] = qty
        session['cart'] = cart

        items, total = get_cart_items()
        cart_count = sum(item['quantity'] for item in items)
        
        return jsonify({'cart_count': cart_count, 'total': total})
    else:
        for key, val in request.form.items():
            if key.startswith('qty_'):
                parts = key.split('_', 1)[1]
                if '_' in parts:
                    mid, pid = parts.rsplit('_', 1)
                    cart_key = f"{mid}:{pid}" if pid != 'none' else mid
                else:
                    cart_key = parts
                
                try:
                    q = int(val)
                    if q > 0:
                        cart[cart_key] = q
                    else:
                        cart.pop(cart_key, None)
                except:
                    pass
        
        session['cart'] = cart
        return redirect(url_for('cart.cart_view'))

@bp.route('/cart/remove/<path:key>', methods=['POST'])
def cart_remove(key):
    cart = session.get('cart', {})
    if key in cart:
        del cart[key]
    session['cart'] = cart
    return redirect(url_for('cart.cart_view'))