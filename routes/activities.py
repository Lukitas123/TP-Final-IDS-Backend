from flask import Blueprint, jsonify
from database import get_db_connection

activities_bp = Blueprint('activities_bp', __name__)

@activities_bp.route('/activity', methods=['GET'])
def get_activities():
    conn = None
    data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM activity ORDER BY id;')
            data = cur.fetchall()
    finally:
        if conn:
            conn.close()
    if not data:
        return jsonify({"status":"error","message":"Tabla 'activity' vacía o no existe"}), 404
    return jsonify({"status":"success","message":"Datos de actividades obtenidos","data": data}), 200
