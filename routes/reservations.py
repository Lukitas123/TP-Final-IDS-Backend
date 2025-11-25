from flask import Blueprint, jsonify, request
from database import get_db_connection
from datetime import datetime

reservations_bp = Blueprint('reservations_bp', __name__)


def _find_available_room(cur, room_type_id, checkin, checkout):
    """
    Busca rápidamente una habitación del tipo pedido que no tenga reservas
    que se solapen con las fechas seleccionadas.
    """
    query = f"""
        SELECT r.id
        FROM room r
        WHERE r.type_id = {room_type_id}
        AND r.id NOT IN (
            SELECT re.room_id
            FROM reservation re
            WHERE re.check_in_date < '{checkout}'
            AND re.check_out_date > '{checkin}'
        )
        ORDER BY r.id
        LIMIT 1;
    """
    cur.execute(query)
    room = cur.fetchone()
    if not room:
        raise ValueError("No quedan habitaciones disponibles de ese tipo para esas fechas")
    return room['id']


def _calculate_reservation_amount(cur, room_id, checkin, checkout, activity_ids, service_ids):
    """
    Suma noches * tarifa + precios de las actividades/servicios seleccionados.
    """
    checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
    checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
    nights = (checkout_date - checkin_date).days
    if nights <= 0:
        raise ValueError("Check-out debe ser posterior a check-in")
    cur.execute(f"SELECT price_per_night FROM room WHERE id={room_id};")
    room_price = cur.fetchone()['price_per_night']
    total = nights * room_price
    if activity_ids:
        cur.execute(f"SELECT COALESCE(SUM(price),0) AS sum FROM activity WHERE id IN ({','.join(map(str,activity_ids))});")
        total += cur.fetchone()['sum']
    if service_ids:
        cur.execute(f"SELECT COALESCE(SUM(price),0) AS sum FROM service WHERE id IN ({','.join(map(str,service_ids))});")
        total += cur.fetchone()['sum']
    return total

@reservations_bp.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    if not data:
        return jsonify({"status":"error","message":"No se recibieron datos"}), 400
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            room_type_id = data.get('room_type_id')
            checkin = data.get('checkin_date')
            checkout = data.get('checkout_date')
            customer_name = data.get('customer_name', '')
            customer_email = data.get('customer_email', '')
            activity_ids = data.get('activity_ids', [])
            service_ids = data.get('service_ids', [])
            package_id = data.get('package_id')

            if not room_type_id or not all([checkin,checkout,customer_name,customer_email]):
                return jsonify({"status":"error","message":"Faltan datos obligatorios"}), 400
            room_id = _find_available_room(cur, room_type_id, checkin, checkout)
            total_amount = _calculate_reservation_amount(cur, room_id, checkin, checkout, activity_ids, service_ids)
            package_sql = 'NULL' if package_id is None else str(package_id)
            cur.execute(f"INSERT INTO reservation (room_id, package_id, check_in_date, check_out_date, amount, customer_name, customer_email) VALUES ({room_id},{package_sql},'{checkin}','{checkout}',{total_amount},'{customer_name}','{customer_email}') RETURNING id;")
            reservation_id = cur.fetchone()['id']
            for aid in activity_ids:
                cur.execute(f"INSERT INTO reservation_activity (reservation_id, activity_id) VALUES ({reservation_id},{aid});")
            for sid in service_ids:
                cur.execute(f"INSERT INTO reservation_service (reservation_id, service_id) VALUES ({reservation_id},{sid});")
            return jsonify({"status":"success","message":"Reserva creada","reservation_id": reservation_id}), 201
    except ValueError as ve:
        return jsonify({"status":"error","message": str(ve)}), 400
    finally:
        if conn:
            conn.close()
