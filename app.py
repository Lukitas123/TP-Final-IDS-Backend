import os
from flask import Flask, jsonify
from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error as Psycopg2Error

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# --- Configuración de la Base de Datos ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No se encontró la variable de entorno DATABASE_URL. Asegúrate de tener un archivo .env con ella.")

def get_db_connection():
    """
    Establece y retorna una conexión a la base de datos PostgreSQL.
    """
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    """
    Ruta principal que también sirve como chequeo de salud de la conexión a la BD.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        return jsonify({"status": "success", "message": "Backend is running and connected to the database."})
    except Psycopg2Error as e:
        # Captura errores específicos de psycopg2 (ej. credenciales incorrectas, host no encontrado)
        return jsonify({
            "status": "error",
            "message": "Failed to connect to the database.",
            "error_details": str(e)
        }), 500
    except Exception as e:
        # Captura cualquier otro error
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred.",
            "error_details": str(e)
        }), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # El host 0.0.0.0 es importante para que sea accesible desde Docker
    app.run(host='0.0.0.0', port=5001, debug=True)
