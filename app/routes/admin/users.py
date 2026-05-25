from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Database
from app.utils.decorators import admin_required

bp = Blueprint('admin_users', __name__, url_prefix='/admin')
# CRUD: Знайти - перегляд списку користувачів
@bp.route('/users')
@admin_required
def admin_users():
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'recent')
    
    sql = 'SELECT * FROM users WHERE 1=1'
    params = []
    
    if search:
        sql += " AND (full_name ILIKE %s OR email ILIKE %s OR phone_number ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    
    if sort == 'name':
        sql += ' ORDER BY full_name ASC'
    elif sort == 'email':
        sql += ' ORDER BY email ASC'
    else:
        sql += ' ORDER BY registration_date DESC'
    
    # CRUD: Знайти - пошук користувачів з фільтрами
    users = Database.fetchall(sql, tuple(params) if params else None)
    return render_template('admin/users.html', users=users, search=search, sort=sort)

@bp.route('/users/search')
@admin_required
def admin_users_search():
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'recent')
    
    sql = 'SELECT * FROM users WHERE 1=1'
    params = []
    
    if search:
        sql += " AND (full_name ILIKE %s OR email ILIKE %s OR phone_number ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    
    if sort == 'name':
        sql += ' ORDER BY full_name ASC'
    elif sort == 'email':
        sql += ' ORDER BY email ASC'
    else:
        sql += ' ORDER BY registration_date DESC'
    
    # CRUD: Знайти - пошук користувачів з фільтрами
    users = Database.fetchall(sql, tuple(params) if params else None)
    return render_template('admin/partials/users_table.html', users=users)

@bp.route('/users/<int:uid>/delete', methods=['POST'])
@admin_required
def admin_user_delete(uid):
    try:
        # CRUD: Видалити - видалення користувача
        Database.execute('DELETE FROM users WHERE user_id=%s', (uid,))
        flash('Користувача видалено')
    except Exception as e:
        flash(f'Помилка: {str(e)}', 'error')
    return redirect(url_for('admin_users.admin_users'))