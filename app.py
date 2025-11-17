import os
from flask import Flask, jsonify
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
    conn = psycopg2.connect(DATABASE_URL)
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
        # Usar RealDictCursor para obtener resultados como diccionarios, y no como tuplas, entonces sé a que columna pertenece cada valor.
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
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
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
