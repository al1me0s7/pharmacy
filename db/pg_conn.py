import os
import psycopg2
from urllib.parse import urlparse
from psycopg2.extras import RealDictCursor
from db.connection import get_db_config

# Функція для отримання підключення до бази даних
def get_conn():
    cfg = get_db_config()

    db_url = os.getenv("DATABASE_URL")

    if db_url:
        result = urlparse(db_url)

        conn = psycopg2.connect(
            dbname=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
    else:
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