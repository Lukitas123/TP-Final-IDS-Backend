from flask import Blueprint, jsonify, request
from database import get_db_connection
from datetime import datetime, timedelta # Added timedelta

reservations_bp = Blueprint('reservations_bp', __name__)


def find_available_room(cur, room_type_id, checkin, checkout):
    """
    Busca rápidamente una habitación del tipo pedido que no tenga reservas
    que se solapen con las fechas seleccionadas.
    """
    query = f"""
        SELECT r.id
        FROM room r
        WHERE r.type_id = {room_type_id}
        AND r.id NOT IN (
            SELECT rr.room_id
            FROM reservation_room rr
            JOIN reservation re ON re.id = rr.reservation_id
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


def calculate_reservation_amount(cur, room_id, checkin, checkout, activity_ids, service_ids):
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
            package_id = data.get('package_id')
            customer_name = data.get('customer_name', '')
            customer_email = data.get('customer_email', '')
            adults = data.get('adults')
            children = data.get('children', 0)

            # Validaciones básicas de pasajeros
            try:
                adults = int(adults)
                children = int(children)
            except (TypeError, ValueError):
                return jsonify({"status":"error","message":"Cantidad de pasajeros inválida"}), 400
            if adults < 1 or children < 0:
                return jsonify({"status":"error","message":"Cantidad de pasajeros inválida"}), 400

            if package_id:
                # --- FLUJO DE RESERVA POR PAQUETE ---
                checkin_str = data.get('checkin_date')
                if not all([checkin_str, customer_name, customer_email]):
                    return jsonify({"status": "error", "message": "Faltan datos obligatorios para la reserva de paquete"}), 400

                # 1. Obtener datos completos del paquete
                cur.execute('SELECT * FROM package WHERE id = %s;', (package_id,))
                package_info = cur.fetchone()
                if not package_info:
                    return jsonify({"status": "error", "message": f"Paquete con ID {package_id} no encontrado"}), 404

                # Obtener el room_type_id del paquete
                cur.execute('SELECT room_type_id FROM package_room_type WHERE package_id = %s LIMIT 1;', (package_id,))
                package_room_type_data = cur.fetchone()
                if not package_room_type_data:
                    return jsonify({"status": "error", "message": f"Paquete con ID {package_id} no tiene tipo de habitación asociado"}), 500
                room_type_id_from_package = package_room_type_data['room_type_id']

                # 2. Calcular checkout_date
                checkin_date_obj = datetime.strptime(checkin_str, '%Y-%m-%d')
                checkout_date_obj = checkin_date_obj + timedelta(days=package_info['nights'])
                checkout_str = checkout_date_obj.strftime('%Y-%m-%d')

                # 3. Encontrar una habitación disponible del tipo de paquete
                room_id = find_available_room(cur, room_type_id_from_package, checkin_str, checkout_str)

                # 4. Usar el precio del paquete como monto total
                total_amount = package_info['price']

                # Insertar en reservation
                cur.execute(
                    f"INSERT INTO reservation (package_id, check_in_date, check_out_date, adults, children, amount, customer_name, customer_email) "
                    f"VALUES ({package_id},'{checkin_str}','{checkout_str}',{adults},{children},{total_amount},'{customer_name}','{customer_email}') RETURNING id;"
                )
                reservation_id = cur.fetchone()['id']

                # Insertar en reservation_room
                cur.execute(f"INSERT INTO reservation_room (reservation_id, room_id) VALUES ({reservation_id},{room_id});")

                # Insertar actividades del paquete en reservation_activity
                cur.execute('SELECT activity_id FROM package_activity WHERE package_id = %s;', (package_id,))
                package_activity_ids = [row['activity_id'] for row in cur.fetchall()]
                for aid in package_activity_ids:
                    cur.execute(f"INSERT INTO reservation_activity (reservation_id, activity_id) VALUES ({reservation_id},{aid});")

                # Insertar servicios del paquete en reservation_service
                cur.execute('SELECT service_id FROM package_service WHERE package_id = %s;', (package_id,))
                package_service_ids = [row['service_id'] for row in cur.fetchall()]
                for sid in package_service_ids:
                    cur.execute(f"INSERT INTO reservation_service (reservation_id, service_id) VALUES ({reservation_id},{sid});")

                conn.commit()
                return jsonify({"status":"success","message":"Reserva de paquete creada","reservation_id": reservation_id, "room_id": room_id }), 201

            else:
                # --- FLUJO DE RESERVA PERSONALIZADA (EXISTENTE) ---
                room_type_id = data.get('room_type_id')
                checkin = data.get('checkin_date')
                checkout = data.get('checkout_date')
                activity_ids = data.get('activity_ids', [])
                service_ids = data.get('service_ids', [])

                if not room_type_id or not all([checkin,checkout,customer_name,customer_email]):
                    return jsonify({"status":"error","message":"Faltan datos obligatorios para la reserva personalizada"}), 400
                
                # Estas validaciones de pasajeros ya se hicieron al inicio, se pueden quitar de aquí
                # try:
                #     adults = int(adults)
                #     children = int(children)
                # except (TypeError, ValueError):
                #     return jsonify({"status":"error","message":"Cantidad de pasajeros inválida"}), 400
                # if adults < 1 or children < 0:
                #     return jsonify({"status":"error","message":"Cantidad de pasajeros inválida"}), 400

                room_id = find_available_room(cur, room_type_id, checkin, checkout)
                total_amount = calculate_reservation_amount(cur, room_id, checkin, checkout, activity_ids, service_ids)
                
                # package_sql will be NULL for personalized reservations
                package_sql = 'NULL' 
                cur.execute(
                    f"INSERT INTO reservation (package_id, check_in_date, check_out_date, adults, children, amount, customer_name, customer_email) "
                    f"VALUES ({package_sql},'{checkin}','{checkout}',{adults},{children},{total_amount},'{customer_name}','{customer_email}') RETURNING id;"
                )
                reservation_id = cur.fetchone()['id']
                for aid in activity_ids:
                    cur.execute(f"INSERT INTO reservation_activity (reservation_id, activity_id) VALUES ({reservation_id},{aid});")
                for sid in service_ids:
                    cur.execute(f"INSERT INTO reservation_service (reservation_id, service_id) VALUES ({reservation_id},{sid});")
                cur.execute(f"INSERT INTO reservation_room (reservation_id, room_id) VALUES ({reservation_id},{room_id});")
                conn.commit()
                return jsonify({"status":"success","message":"Reserva personalizada creada","reservation_id": reservation_id, "room_id": room_id }), 201
    except ValueError as ve:
        return jsonify({"status":"error","message": str(ve)}), 400
    finally:
        if conn:
            conn.close()
