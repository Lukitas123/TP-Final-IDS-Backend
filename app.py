import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error as Psycopg2Error
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)

#Configuración de la Base de Datos
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No se encontró la variable de entorno DATABASE_URL. Asegúrate de tener un archivo .env con ella.")

def get_db_connection():
    # Usar RealDictCursor para obtener resultados como diccionarios, y no como tuplas, entonces sé a que columna pertenece cada valor.
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

#Rutas de la Aplicación
@app.route('/')
def index():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
    except Psycopg2Error as db_err:
        return jsonify({
            "status": "error",
            "message": "Error de base de datos al verificar conexión.",
            "error_details": str(db_err)
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Error inesperado al verificar conexión.",
            "error_details": str(e)
        }), 500
    finally:
        if conn:
            conn.close()
    return jsonify({"status": "success", "message": "Back funcionando y conectado a la BDD"}), 200

@app.route('/rooms', methods=['GET'])
def get_rooms():
    conn = None
    rooms_data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM room r ORDER BY r.id;')
            rooms_data = cur.fetchall()
    except Psycopg2Error as db_err:
        return jsonify({
            "status": "error",
            "message": "Error de base de datos al obtener datos de la tabla 'room'",
            "error_details": str(db_err)
        }), 500
    except Exception as err:
        return jsonify({
            "status": "error",
            "message": "Error inesperado al obtener datos de la tabla 'room'",
            "error_details": str(err)
        }), 500
    finally:
        if conn:
            conn.close()

    if not rooms_data:
        return jsonify({
            "status": "error",
            "message": "La tabla 'room' está vacía o no existe."
        }), 404
    
    print(f"Datos obtenidos de la tabla 'room':\n{rooms_data}")
    return jsonify({"status": "success", "message": "Conexión a la BDD exitosa - Tabla Rooms accesible", "data": rooms_data}), 200

@app.route('/room_types', methods=['GET'])
def get_room_types():
    conn = None
    room_types_data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM room_type ORDER BY id;')
            room_types_data = cur.fetchall()
    except Psycopg2Error as db_err:
        return jsonify({
            "status": "error",
            "message": "Error de base de datos al obtener datos de la tabla 'room_type'",
            "error_details": str(db_err)
        }), 500
    except Exception as err:
        return jsonify({
            "status": "error",
            "message": "Error inesperado al obtener datos de la tabla 'room_type'",
            "error_details": str(err)
        }), 500
    finally:
        if conn:
            conn.close()

    if not room_types_data:
        return jsonify({
            "status": "error",
            "message": "La tabla 'room_type' está vacía o no existe."
        }), 404
    
    return jsonify({
        "status": "success",
        "message": "Datos de tipos de habitación obtenidos con éxito.",
        "data": room_types_data
    }), 200

@app.route('/availability', methods=['GET'])
def get_availability():
    checkin_date = request.args.get('checkin')
    checkout_date = request.args.get('checkout')
    
    if not checkin_date or not checkout_date:
        return jsonify({
            "status": "error",
            "message": "Faltan parámetros obligatorios 'checkin' o 'checkout' (I'm a teapot)."
        }), 418
    
    conn = None
    availability_data = None
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
            cur.execute(query, vars=(checkout_date, checkin_date))
            availability_data = cur.fetchall()
    except Psycopg2Error as db_err:
        return jsonify({
            "status": "error",
            "message": "Error de base de datos al obtener datos de la tabla 'availability'",
            "error_details": str(db_err)
        }), 500        
    except Exception as err:
        return jsonify({
            "status": "error",
            "message": "Error inesperado al obtener datos de la tabla 'availability'",
            "error_details": str(err)
        }), 500
    finally:
        if conn:
            conn.close()

    if not availability_data:
        return jsonify({
            "status": "error",
            "message": "No hay habitaciones disponibles para las fechas proporcionadas.",
            "data": []
        }), 404
    
    return jsonify({
        "status": "success",
        "message": "Datos de disponibilidad obtenidos con éxito.",
        "data": availability_data
    }), 200

@app.route('/activity', methods=['GET'])
def get_activities():
    conn = None
    activities_data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM activity ORDER BY id;')
            activities_data = cur.fetchall()
    except Psycopg2Error as db_err:
        return jsonify({
            "status": "error",
            "message": "Error de base de datos al obtener datos de la tabla 'activity'",
            "error_details": str(db_err)
        }), 500
    except Exception as err:
        return jsonify({
            "status": "error",
            "message": "Error inesperado al obtener datos de la tabla 'activity'",
            "error_details": str(err)
        }), 500
    finally:
        if conn:
            conn.close()

    if not activities_data:
        return jsonify({
            "status": "error",
            "message": "La tabla 'activity' está vacía o no existe."
        }), 404
    
    return jsonify({
        "status": "success",
        "message": "Datos de actividades obtenidos con éxito.",
        "data": activities_data
    }), 200

@app.route('/services', methods=['GET'])
def get_services():
    conn = None
    services_data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM service ORDER BY id;')
            services_data = cur.fetchall()
    except Psycopg2Error as db_err:
        return jsonify({
            "status": "error",
            "message": "Error de base de datos al obtener datos de la tabla 'service'",
            "error_details": str(db_err)
        }), 500
    except Exception as err:
        return jsonify({
            "status": "error",
            "message": "Error inesperado al obtener datos de la tabla 'service'",
            "error_details": str(err)
        }), 500
    finally:
        if conn:
            conn.close()

    if not services_data:
        return jsonify({
            "status": "error",
            "message": "La tabla 'service' está vacía o no existe."
        }), 404
    
    return jsonify({
        "status": "success",
        "message": "Datos de servicios obtenidos con éxito.",
        "data": services_data
    }), 200

@app.route('/package', methods=['GET'])
def get_packages():
    conn = None
    packages_data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM package ORDER BY id;')
            packages_data = cur.fetchall()
    except Psycopg2Error as db_err:
        return jsonify({
            "status": "error",
            "message": "Error de base de datos al obtener datos de la tabla 'package'",
            "error_details": str(db_err)
        }), 500
    except Exception as err:
        return jsonify({
            "status": "error",
            "message": "Error inesperado al obtener datos de la tabla 'package'",
            "error_details": str(err)
        }), 500
    finally:
        if conn:
            conn.close()

    if not packages_data:
        return jsonify({
            "status": "error",
            "message": "La tabla 'package' está vacía o no existe."
        }), 404
    
    return jsonify({
        "status": "success",
        "message": "Datos de packs obtenidos con éxito.",
        "data": packages_data
    }), 200

def _calculate_reservation_amount(cur, room_id, checkin_date_str, checkout_date_str, activity_ids, service_ids):
    checkin_date_obj = datetime.strptime(checkin_date_str, '%Y-%m-%d')
    checkout_date_obj = datetime.strptime(checkout_date_str, '%Y-%m-%d')
    nights = (checkout_date_obj - checkin_date_obj).days
    if nights <= 0:
        raise ValueError("La fecha de check-out debe ser posterior a la de check-in.")

    # Obtener precio por noche de la habitación
    query_room_price = "SELECT price_per_night FROM room WHERE id = " + str(room_id) + ";"
    cur.execute(query_room_price)
    room_price_per_night = cur.fetchone()['price_per_night']

    total_amount = nights * room_price_per_night

    # Sumar precios de actividades
    if activity_ids:
        activity_ids_str = ",".join(map(str, activity_ids))
        query_activity_price = "SELECT COALESCE(SUM(price), 0) as sum FROM activity WHERE id IN (" + activity_ids_str + ");"
        cur.execute(query_activity_price)
        total_amount += cur.fetchone()['sum']
    
    # Sumar precios de servicios
    if service_ids:
        service_ids_str = ",".join(map(str, service_ids))
        query_service_price = "SELECT COALESCE(SUM(price), 0) as sum FROM service WHERE id IN (" + service_ids_str + ");"
        cur.execute(query_service_price)
        total_amount += cur.fetchone()['sum']

    return total_amount

@app.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No se recibió ningún dato."}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            package_id = data.get('package_id')
            room_type_id = data.get('room_type_id')
            checkin_date_str = data.get('checkin_date')
            checkout_date_str = data.get('checkout_date')
            
            customer_name = data.get('customer_name', '')
            customer_email = data.get('customer_email', '')
            
            activity_ids = data.get('activity_ids', [])
            service_ids = data.get('service_ids', [])
            
            if not room_type_id:
                 return jsonify({"status": "error", "message": "Se requiere 'room_type_id' para la reserva."}), 400
            if not all([checkin_date_str, checkout_date_str, customer_name, customer_email]):
                 return jsonify({"status": "error", "message": "Faltan datos obligatorios de la reserva (fechas, nombre, email)."}), 400

            #Búsqueda de Habitación SÚPER SIMPLE
            query_room_search = "SELECT id, price_per_night FROM room WHERE type_id = " + str(room_type_id) + " LIMIT 1;"
            cur.execute(query_room_search)
            room_to_book = cur.fetchone()

            if not room_to_book:
                return jsonify({"status": "error", "message": "No existen habitaciones del tipo solicitado."}), 404
            
            room_id = room_to_book['id']

            #Cálculo del Monto Total
            total_amount = _calculate_reservation_amount(
                cur, room_id, checkin_date_str, checkout_date_str, activity_ids, service_ids
            )

            #INSERCIÓN EN BASE DE DATOS
            package_id_sql = 'NULL' if package_id is None else str(package_id)
            
            insert_query_reservation = "INSERT INTO reservation (room_id, package_id, check_in_date, check_out_date, adults, children, amount, customer_name, customer_email) VALUES (" \
                                        + str(room_id) + ", " + package_id_sql + ", '" + checkin_date_str + "', '" + checkout_date_str + "', " \
                                        + ", " + str(total_amount) + ", '" + customer_name + "', '" + customer_email + "') RETURNING id;"
            cur.execute(insert_query_reservation)
            reservation_id = cur.fetchone()['id']

            for activity_id in activity_ids:
                cur.execute("INSERT INTO reservation_activity (reservation_id, activity_id) VALUES (" + str(reservation_id) + ", " + str(activity_id) + ");")
            for service_id in service_ids:
                cur.execute("INSERT INTO reservation_service (reservation_id, service_id) VALUES (" + str(reservation_id) + ", " + str(service_id) + ");")

            return jsonify({"status": "success", "message": "Reserva creada con éxito (método INSEGURO con concatenación).", "reservation_id": reservation_id}), 201

    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as err:
        return jsonify({"status": "error", "message": "Error inesperado.", "error_details": str(err)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)