from flask import Blueprint, jsonify
from database import get_db_connection
from psycopg2 import Error as Psycopg2Error

rooms_bp = Blueprint('rooms_bp', __name__)

@rooms_bp.route('/rooms', methods=['GET'])
def get_rooms():
    conn = None
    rooms_data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM room ORDER BY id;')
            rooms_data = cur.fetchall()
    except Psycopg2Error as db_err:
        return jsonify({"status":"error","message":"Error DB al obtener rooms","error_details": str(db_err)}), 500
    finally:
        if conn:
            conn.close()
    if not rooms_data:
        return jsonify({"status":"error","message":"Tabla 'room' vacía o no existe"}), 404
    return jsonify({"status":"success","message":"Datos de rooms obtenidos","data": rooms_data}), 200
