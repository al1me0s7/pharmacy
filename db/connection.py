DB_USER = 'postgres'
DB_PASSWORD = 'al1niaml'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'pharmacy'

# Функція для отримання бази даних
def get_db_uri():
    return f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Функція для отримання параметрів підключення
def get_db_config():
    return {
        'dbname': DB_NAME,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'host': DB_HOST,
        'port': DB_PORT,
    }