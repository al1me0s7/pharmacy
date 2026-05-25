from app.routes.main import bp as main_bp
from app.routes.auth import bp as auth_bp
from app.routes.cart import bp as cart_bp
from app.routes.orders import bp as orders_bp
from app.routes.bookings import bp as bookings_bp
from app.routes.profile import bp as profile_bp
from app.routes.admin.auth import bp as admin_auth_bp
from app.routes.admin.dashboard import bp as admin_dashboard_bp
from app.routes.admin.medicines import bp as admin_medicines_bp
from app.routes.admin.users import bp as admin_users_bp
from app.routes.admin.categories import bp as admin_categories_bp
from app.routes.admin.manufacturers import bp as admin_manufacturers_bp
from app.routes.admin.orders import bp as admin_orders_bp
from app.routes.admin.bookings import bp as admin_bookings_bp
from app.routes.admin.pharmacies import bp as admin_pharmacies_bp
from app.routes.admin.inventory import bp as admin_inventory_bp

def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_auth_bp)
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_medicines_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_categories_bp)
    app.register_blueprint(admin_manufacturers_bp)
    app.register_blueprint(admin_orders_bp)
    app.register_blueprint(admin_bookings_bp)
    app.register_blueprint(admin_pharmacies_bp)
    app.register_blueprint(admin_inventory_bp)