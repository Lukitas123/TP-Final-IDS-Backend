from flask import Blueprint, jsonify
from database import get_db_connection
from psycopg2 import Error as Psycopg2Error

home_bp = Blueprint('home_bp', __name__)

@home_bp.route('/')
def index():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
    except Psycopg2Error as db_err:
        return jsonify({"status":"error","message":"Error DB al verificar conexión","error_details": str(db_err)}), 500
    except Exception as e:
        return jsonify({"status":"error","message":"Error inesperado al verificar conexión","error_details": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify({"status": "success", "message": "Back funcionando y conectado a la BDD"}), 200
