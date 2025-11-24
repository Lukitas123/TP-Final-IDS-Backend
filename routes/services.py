from flask import Blueprint, jsonify
from database import get_db_connection

services_bp = Blueprint('services_bp', __name__)

@services_bp.route('/services', methods=['GET'])
def get_services():
    conn = None
    data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM service ORDER BY id;')
            data = cur.fetchall()
    finally:
        if conn:
            conn.close()
    if not data:
        return jsonify({"status":"error","message":"Tabla 'service' vacía o no existe"}), 404
    return jsonify({"status":"success","message":"Datos de servicios obtenidos","data": data}), 200
