from flask import Blueprint, request, jsonify
from database import get_db_connection

services_bp = Blueprint('services_bp', __name__)

def get_room_types_post(conn,cur):
    query = """
        INSERT INTO service (name, description, price)
        VALUES (%s, %s, %s)
    """
    data_new = request.json
    name_new = data_new.get("name")
    description_new = data_new.get("description")
    price_new = data_new.get("price")
    if (not (name_new and description_new and price_new)):
        return jsonify({
            "status": "error",
            "message": "No se ingresaron los datos correctamente",
            }), 409
    #409 Conflict: El request no se pudo completar debido a un conflicto con el estado actual del recurso
    else:
        cur.execute(query,(name_new, description_new, price_new))
        conn.commit()
        return jsonify({
            "status": "success",
            "message": "Datos cargados con éxito",
            }),200

@services_bp.route('/services', methods=['GET', 'POST'])
def get_services():
    conn = None
    data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:

            if (request.method == 'POST'):
                get_room_types_post(conn,cur)
                cur.close()
            else:
                #Si es GET
                cur.execute('SELECT * FROM service ORDER BY id;')
                data = cur.fetchall()
                cur.close()

                if not data:
                    return jsonify({"status":"error","message":"Tabla 'service' vacía o no existe"}), 404
                else:
                    return jsonify({"status":"success","message":"Datos de servicios obtenidos","data": data}), 200
    finally:
        if conn:
            conn.close()