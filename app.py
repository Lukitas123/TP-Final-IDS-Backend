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
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        return jsonify({"status": "success", "message": "Back funcionando y conectado a la BDD"})
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
            
@app.route('/rooms', methods=['GET'])
def get_rooms():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM room r ORDER BY r.id;')
        
        rooms_data = cur.fetchall()
        if not rooms_data:
            return jsonify({
                "status": "error",
                "message": "La tabla 'room' está vacía o no existe."
            }), 404
        
        print(f"Datos obtenidos de la tabla 'room':\n{rooms_data}")
        cur.close()
        return jsonify({"status": "success", "message": "Conexión a la BDD exitosa - Tabla Rooms accesible", "data": rooms_data}), 200
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

@app.route('/room_type', methods=['GET'])
def get_room_types():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM room_type ORDER BY id;')
        
        room_types_data = cur.fetchall()
        
        if not room_types_data:
            return jsonify({
                "status": "error",
                "message": "La tabla 'room_type' está vacía o no existe."
            }), 404
        
        cur.close()
        return jsonify({
            "status": "success",
            "message": "Datos de tipos de habitación obtenidos con éxito.",
            "data": room_types_data
        }), 200
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

@app.route('/availability', methods=['POST'])
def get_availability():
    """
    Endpoint para obtener la disponibilidad de tipos de habitación en base a fechas de check-in y check-out.
    Parámetros esperados en la query string:
    - checkin: Fecha de check-in en formato 'YYYY-MM-DD'
    - checkout: Fecha de check-out en formato 'YYYY-MM-DD'
    """
    checkin_date = request.args.get('checkin')
    checkout_date = request.args.get('checkout')
    
    if not checkin_date or not checkout_date:
        return jsonify({
            "status": "error",
            "message": 'Faltan parámetros obligatorios ''checkin'' o ''checkout'' (I`m a teapot).'
        }), 418
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Es una query compleja, que obtiene los tipos de habitación disponibles en base a las reservas ya existentes.
        # La lógica es: Seleccionar todos los tipos de habitación asociados a habitaciones que no estén reservadas en el rango de fechas dado.
        # Hay dos casos:
        # 1) La fecha de mi salida es luego de la fecha de entrada de una reserva existente (existing_checkin < checkout_date)
        # 2) La fecha de mi entrada es antes de la fecha de salida de una reserva existente (existing_checkout > checkin_date)
        # Si ambos casos se cumplen, significa que hay un solapamiento y la habitación no está disponible.
        # Por lo tanto, excluimos esas habitaciones de nuestra selección.
        # Finalmente, agrupamos por tipo de habitación para evitar duplicados. 
        # Se usa %s porque funciona como placeholder para psycopg2, evitando inyecciones SQL (Chequea el tipo de dato antes de construir la query).
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
        
        if not availability_data:
            return jsonify({
                "status": "error",
                "message": "No hay habitaciones disponibles para las fechas proporcionadas."
                "data": []
            }), 404

        
        cur.close()
        return jsonify({
            "status": "success",
            "message": "Datos de disponibilidad obtenidos con éxito.",
            "data": availability_data
        }), 200
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
