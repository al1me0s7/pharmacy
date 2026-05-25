# Інформаційна система "Аптека" 

Веб-застосунок для автоматизації процесів пошуку, замовлення та бронювання лікарських засобів. Курсовий проєкт з дисципліни "Бази даних".

## Основні функції

### Для користувачів:
- Перегляд каталогу ліків з фільтрацією (категорія, виробник, місто, рецептурність)
- Пошук препаратів за назвою
- Порівняння цін у різних аптеках
- Оформлення замовлень (для безрецептурних ліків)
- Бронювання рецептурних препаратів з самовивозом
- Перегляд історії транзакцій
- Генерація PDF-чеків
- Залишення відгуків про препарати

### Для адміністраторів:
- Управління каталогом ліків (CRUD операції)
- Управління довідниками (категорії, виробники, аптеки, міста)
- Перегляд та зміна статусів замовлень/бронювань
- Генерація аналітичних звітів (PDF) за період
- Перегляд статистики продажів

## Технології

- Backend: Python 3.11, Flask 3.0
- Database: PostgreSQL 15
- Frontend: HTML5, CSS3, Bootstrap 5, Jinja2
- PDF Generation: ReportLab
- DB Client: DBeaver Community Edition

## Інструкця по встановленню

## Крок 1: Клонування репозиторію
```bash
git clone <repository-url>
cd pharmacy-project
```

## Крок 2: Створення віртуального середовища

**Windows (cmd.exe):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## Крок 3: Встановлення залежностей
```bash
pip install -r requirements.txt
```

## Крок 4: Налаштування бази даних PostgreSQL

1. **Встановіть PostgreSQL 15** (якщо не встановлено):
   - Windows: https://www.postgresql.org/download/windows/
   - Linux: `sudo apt install postgresql postgresql-contrib`
   - macOS: `brew install postgresql@15`

2. **Створіть базу даних:**
```sql
CREATE DATABASE pharmacy_db;
```

3. **Налаштуйте підключення:**
   - Відкрийте файл `db/connection.py`
   - Вкажіть свої параметри підключення:
```python
DB_USER = "postgres"         # Ваш користувач PostgreSQL
DB_PASSWORD = "your_password" # Ваш пароль
DB_NAME = "pharmacy_db"       # Назва бази даних
DB_HOST = "localhost"
DB_PORT = "5432"
```

## Крок 5: Ініціалізація бази даних

**Варіант А: Використання бекапу (краще)**

У папці `backup/` знаходиться повний дамп бази даних з тестовими даними.

**Через DBeaver:**
1. Підключіться до бази `pharmacy_db`
2. ПКМ на базі → Tools → Execute script
3. Оберіть файл `backup/pharmacy_backup.sql`
4. Виконайте скрипт

**Через термінал PostgreSQL:**
```bash
# Windows
psql -U postgres -d pharmacy_db -f backup/pharmacy_backup.sql

# Linux/macOS
psql -U postgres -d pharmacy_db < backup/pharmacy_backup.sql
```

**Варіант Б: Вручну створити структуру**

Якщо бекап не працює, виконайте міграції:
```bash
python migrations/run_migrations.py
```

## Крок 6: Запуск застосунку
```bash
python run.py
```

Або через Flask CLI:
```bash
set FLASK_APP=run.py  # Windows cmd
export FLASK_APP=run.py  # Linux/macOS
flask run
```

Застосунок буде доступний за адресою: **http://127.0.0.1:5000/**


## тестові облікові записи

**Адміністратор:**
- Логін: `admin`
- Пароль: `admin123`

**Користувач:**
- Email: `user@example.com`
- Пароль: `user123`


## Здобувач
Студент групи ПЗПІ-24-7  
Харківський національний університет радіоелектроніки  
Османова Аліме Ділаверівна