import psycopg2
from psycopg2.extras import RealDictCursor
from db.connection import get_db_config

# Функція для отримання підключення до бази даних
def get_conn():
    cfg = get_db_config()

    conn = psycopg2.connect(
        dbname=cfg['dbname'],
        user=cfg['user'],
        password=cfg['password'],
        host=cfg.get('host', 'localhost'),
        port=cfg.get('port', '5432')
    )
    return conn

def get_cursor_dict(conn):
    return conn.cursor(cursor_factory=RealDictCursor)