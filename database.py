import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("No se encontró DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn
