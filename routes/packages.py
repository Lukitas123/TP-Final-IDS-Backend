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

@packages_bp.route('/package/<int:package_id>', methods=['GET'])
def get_package_by_id(package_id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # 1. Obtener datos base del paquete
            cur.execute('SELECT * FROM package WHERE id = %s;', (package_id,))
            package_data = cur.fetchone()
            if not package_data:
                return jsonify({"status": "error", "message": "Paquete no encontrado"}), 404

            # 2. Obtener tipo de habitación (asumiendo uno por paquete)
            cur.execute(
                'SELECT rt.id, rt.name, rt.description, rt.gallery FROM room_type rt JOIN package_room_type prt ON rt.id = prt.room_type_id WHERE prt.package_id = %s LIMIT 1;',
                (package_id,)
            )
            room_type_data = cur.fetchone()
            package_data['room_type'] = room_type_data

            # 3. Obtener actividades
            cur.execute(
                'SELECT a.id, a.name, a.description, a.price, a.gallery, a.schedule FROM activity a JOIN package_activity pa ON a.id = pa.activity_id WHERE pa.package_id = %s;',
                (package_id,)
            )
            package_data['activities'] = cur.fetchall()

            # 4. Obtener servicios
            cur.execute(
                'SELECT s.id, s.name, s.description, s.price, s.gallery FROM service s JOIN package_service ps ON s.id = ps.service_id WHERE ps.package_id = %s;',
                (package_id,)
            )
            package_data['services'] = cur.fetchall()

            return jsonify({"status": "success", "data": package_data}), 200
    finally:
        if conn:
            conn.close()
