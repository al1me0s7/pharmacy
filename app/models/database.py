import psycopg2
from psycopg2.extras import RealDictCursor
from db.pg_conn import get_conn

class Database:
    @staticmethod
    def fetchall(sql, params=None):
        conn = get_conn()
        cur = get_cursor_dict(conn)
        cur.execute(sql, tuple(params) if params else ())
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    @staticmethod
    def fetchone(sql, params=None):
        conn = get_conn()
        cur = get_cursor_dict(conn)
        cur.execute(sql, params or ())
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row

    @staticmethod
    def execute(sql, params=None, returning=False):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, params or ())
        val = None
        if returning:
            val = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return val

def get_cursor_dict(conn):
    return conn.cursor(cursor_factory=RealDictCursor)