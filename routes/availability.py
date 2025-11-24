from flask import Blueprint, jsonify, request
from database import get_db_connection
from psycopg2 import Error as Psycopg2Error

availability_bp = Blueprint('availability_bp', __name__)

@availability_bp.route('/availability', methods=['GET'])
def get_availability():
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')
    if not checkin or not checkout:
        return jsonify({"status":"error","message":"Faltan parámetros 'checkin' o 'checkout'"}), 418
    conn = None
    data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            query = """
                SELECT rt.*
                FROM room_type rt
                INNER JOIN room rm
                ON rt.id = rm.type_id
                WHERE rm.id NOT IN (
                    SELECT re.room_id
                    FROM reservation re 
                    WHERE re.check_in_date < %s
                    AND re.check_out_date > %s
                )
                GROUP BY rt.id;
            """
            cur.execute(query, (checkout, checkin))
            data = cur.fetchall()
    except Psycopg2Error as db_err:
        return jsonify({"status":"error","message":"Error DB al obtener disponibilidad","error_details": str(db_err)}), 500
    finally:
        if conn:
            conn.close()
    if not data:
        return jsonify({"status":"error","message":"No hay habitaciones disponibles","data": []}), 404
    return jsonify({"status":"success","message":"Disponibilidad obtenida","data": data}), 200
