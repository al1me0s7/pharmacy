from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.admin import Admin

bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

@bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        
        if not login or not password:
            flash('Введіть логін та пароль', 'error')
            return render_template('admin/login.html')
        
        # CRUD: Знайти - пошук адміністратора за логіном
        admin = Admin.find_by_login(login)
        if admin and Admin.verify_password(admin, password):
            session['admin'] = True
            session['admin_user'] = admin
            flash('Вхід успішний', 'success')
            return redirect(url_for('admin_dashboard.admin_dashboard'))
        else:
            flash('Невірний логін або пароль', 'error')
    
    return render_template('admin/login.html')

@bp.route('/logout')
def admin_logout():
    session.pop('admin', None)
    session.pop('admin_user', None)
    flash('Вихід успішний', 'success')
    return redirect(url_for('main.index'))