from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Database
from app.utils.decorators import admin_required
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify

bp = Blueprint('admin_categories', __name__, url_prefix='/admin')

@bp.route('/categories')
@admin_required
def admin_categories():
    search = request.args.get('search', '').strip()
    # CRUD: перегляд списку категорій
    sql = 'SELECT * FROM categories WHERE 1=1'
    params = []
    
    if search:
        sql += " AND category_name ILIKE %s"
        params.append(f'%{search}%')
    
    sql += ' ORDER BY category_name ASC'
    
    # CRUD:  пошук категорій
    categories = Database.fetchall(sql, tuple(params) if params else None)
    return render_template('admin/categories.html', categories=categories, search=search)

@bp.route('/categories/search')
@admin_required
def admin_categories_search():
    search = request.args.get('search', '').strip()
    
    sql = 'SELECT * FROM categories WHERE 1=1'
    params = []
    
    if search:
        sql += " AND category_name ILIKE %s"
        params.append(f'%{search}%')
    
    sql += ' ORDER BY category_name ASC'
    
    # CRUD: Знайти - пошук категорій
    categories = Database.fetchall(sql, tuple(params) if params else None)
    return render_template('admin/partials/categories_table.html', categories=categories)

@bp.route('/categories/add', methods=['GET', 'POST'])
@admin_required
def admin_categories_add():
    if request.method == 'POST':
        category_name = request.form.get('category_name', '').strip()
        description = request.form.get('description', '').strip()

        if not category_name:
            flash('Назва категорії обов\'язкова', 'error')
            return redirect(url_for('admin_categories.admin_categories_add'))

        try:
            Database.execute(
                'INSERT INTO categories (category_name, description) VALUES (%s, %s)',
                (category_name, description)
            )
            flash('Категорію додано')
            return redirect(url_for('admin_categories.admin_categories'))
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')

    return render_template('admin/categories_add.html')


@bp.route('/categories/<int:cid>/edit', methods=['GET', 'POST'])
@admin_required
def admin_categories_edit(cid):
    if request.method == 'POST':
        category_name = request.form.get('category_name', '').strip()
        description = request.form.get('description', '').strip()

        if not category_name:
            flash('Назва категорії обов\'язкова', 'error')
            return redirect(url_for('admin_categories.admin_categories_edit', cid=cid))

        try:
            Database.execute(
                'UPDATE categories SET category_name=%s, description=%s WHERE category_id=%s',
                (category_name, description, cid)
            )
            flash('Категорію оновлено')
            return redirect(url_for('admin_categories.admin_categories'))
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')

    category = Database.fetchone('SELECT * FROM categories WHERE category_id=%s', (cid,))
    if not category:
        flash('Категорію не знайдено', 'error')
        return redirect(url_for('admin_categories.admin_categories'))

    return render_template('admin/categories_edit.html', category=category)


@bp.route('/categories/<int:cid>/delete', methods=['POST'])
@admin_required
def admin_categories_delete(cid):
    try:
        # CRUD: Знайти - перевірка наявності ліків у категорії
        medicines = Database.fetchall(
            'SELECT medicine_id, name FROM medicines WHERE category_id=%s ORDER BY name',
            (cid,)
        )
        
        # Якщо в категорії є ліки - не видаляємо!
        if medicines and len(medicines) > 0:
            med_names = ', '.join([f"'{m.get('name', 'N/A')}'" for m in medicines])
            flash(
                f'Не можна видалити категорію!\n\n'
                f'В цій категорії є {len(medicines)} ліків:\n'
                f'{med_names}\n\n'
                f'Спочатку видаліть або змініть категорію для цих ліків.',
                'error'
            )
            return redirect(url_for('admin_categories.admin_categories'))
        
        # Видалити категорію (тільки якщо немає ліків)
        Database.execute('DELETE FROM categories WHERE category_id=%s', (cid,))
        flash('✓ Категорію успішно видалено')
    except Exception as e:
        flash(f'Помилка при видаленні категорії: {str(e)}', 'error')
    
    return redirect(url_for('admin_categories.admin_categories'))

@bp.route('/categories/<int:cid>/check_medicines')
@admin_required
def check_medicines(cid):
    row = Database.fetchone(
        "SELECT COUNT(*) as cnt FROM medicines WHERE category_id = %s",
        (cid,)
    )
    cnt = row['cnt'] if row else 0
    return jsonify({
        'has_medicines': cnt > 0,
        'medicines_count': cnt
    })