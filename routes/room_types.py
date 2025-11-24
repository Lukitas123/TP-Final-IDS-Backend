from flask import Blueprint, jsonify
from database import get_db_connection
from psycopg2 import Error as Psycopg2Error

room_types_bp = Blueprint('room_types_bp', __name__)

@room_types_bp.route('/room_types', methods=['GET'])
def get_room_types():
    conn = None
    data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM room_type ORDER BY id;')
            data = cur.fetchall()
    except Psycopg2Error as db_err:
        return jsonify({"status":"error","message":"Error DB al obtener room_types","error_details": str(db_err)}), 500
    finally:
        if conn:
            conn.close()
    if not data:
        return jsonify({"status":"error","message":"Tabla 'room_type' vacía o no existe"}), 404
    return jsonify({"status":"success","message":"Datos de room_type obtenidos","data": data}), 200
