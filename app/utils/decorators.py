from flask import session, redirect, url_for
from functools import wraps

# для захисту адміністративних маршрутів 
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_auth.admin_login'))
        return f(*args, **kwargs)
    return wrapper