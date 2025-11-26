from flask import Blueprint, jsonify, request
from database import get_db_connection
from psycopg2 import Error as Psycopg2Error

activities_bp = Blueprint('activities_bp', __name__)

@activities_bp.route('/activity', methods=['GET', 'POST'])
def get_activities():
    conn = None
    data = None
    data_new = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if (request.method == 'POST'):
                query = """
                    INSERT INTO activity (name, description, price, gallery, schedule)
                    VALUES (%s, %s, %s, %s, %s)
                """
                data_new = request.json
                name_new = data_new.get("name")
                description_new = data_new.get("description")
                price_new = data_new.get("price")
                gallery_new = data_new.get("gallery")
                schedule_new = data_new.get("schedule")
                if (not (name_new and description_new and price_new and gallery_new and schedule_new)):
                    return jsonify({
                        "status": "error",
                        "message": "No se ingresaron los datos correctamente",
                    }), 409
                #409 Conflict: El request no se pudo completar debido a un conflicto con el estado actual del recurso
                else:
                    cur.execute(query,(name_new, description_new, price_new, gallery_new, schedule_new))
                    conn.commit()
                    return jsonify({
                        "status": "success",
                        "message": "Datos cargados con éxito",
                    })
                cur.close()
            else:
                #Si es GET
                cur.execute('SELECT * FROM activity ORDER BY id;')
                data = cur.fetchall()
                cur.close()

                if not data:
                    return jsonify({"status":"error","message":"Tabla 'activity' vacía o no existe"}), 404
                else:
                    return jsonify({"status":"success","message":"Datos de actividades obtenidos","data": data}), 200
                
    except Psycopg2Error as db_err:
        return jsonify({"status":"error","message":"Error DB al obtener activities","error_details": str(db_err)}), 500
    finally:
        if conn:
            conn.close()         