import os
from flask import Flask, jsonify
from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error as Psycopg2Error
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
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Error inesperado",
            "error_details": str(e)
        }), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
