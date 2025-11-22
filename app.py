import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error as Psycopg2Error
from psycopg2.extras import RealDictCursor
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

@app.route('/api/activity', methods=['GET'])
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

@app.route('/api/services', methods=['GET'])
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

@app.route('/api/package', methods=['GET'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
