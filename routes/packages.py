from flask import Blueprint, jsonify
from database import get_db_connection

packages_bp = Blueprint('packages_bp', __name__)

@packages_bp.route('/package', methods=['GET'])
def get_packages():
    conn = None
    data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM package ORDER BY id;')
            data = cur.fetchall()
    finally:
        if conn:
            conn.close()
    if not data:
        return jsonify({"status":"error","message":"Tabla 'package' vacía o no existe"}), 404
    return jsonify({"status":"success","message":"Datos de packs obtenidos","data": data}), 200
