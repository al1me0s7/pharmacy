from flask import Flask
from app.config import Config
from app.routes import register_routes
from app.utils.helpers import get_current_user, get_cart_items, translate_order_status, translate_delivery_method

# Функція для створення Фласк-додатку
def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

    register_routes(app)

    # Глобальні змінні для шаблонів
    @app.context_processor
    def inject_globals():
        user = get_current_user()
        cart_items, cart_total = get_cart_items()
        cart_count = sum(item['quantity'] for item in cart_items)
        return {
            'current_user': user,
            'cart_count': cart_count,
            'cart_total': cart_total,
            'translate_order_status': translate_order_status,
            'translate_delivery_method': translate_delivery_method
        }

    # Обробник 404
    from flask import render_template
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app