from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import User

bp = Blueprint('auth', __name__)
# CRUD: Створити - реєстрація користувача
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            User.create(
                full_name=request.form.get('full_name'),
                email=request.form.get('email'),
                password=request.form.get('password'),
                phone=request.form.get('phone'),
                address=request.form.get('address'),
                city=request.form.get('city'),
                postal_code=request.form.get('postal_code')
            )
            user = User.find_by_email(request.form.get('email'))
            session['user_id'] = user['user_id']
            flash('Реєстрація пройшла успішно! ✓')
            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f'Помилка реєстрації: {str(e)}')
            return render_template('auth.html', show_register=True) 
    
    return render_template('auth.html', show_register=True)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.find_by_email(email)
        
        if user and User.verify_password(user, password):
            session['user_id'] = user['user_id']
            flash('Вхід успішний!')
            return redirect(url_for('main.index'))
        else:
            flash('Невірний email або пароль')
            return render_template('auth.html', show_register=False)
    
    return render_template('auth.html', show_register=False)

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('cart', None)
    flash('Ви вийшли з системи')
    return redirect(url_for('main.index'))