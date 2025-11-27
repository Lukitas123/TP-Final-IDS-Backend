from flask import Blueprint, jsonify, request
from database import get_db_connection
from psycopg2 import Error as Psycopg2Error

room_types_bp = Blueprint('room_types_bp', __name__)

def get_room_types_post(conn,cur):
      query = """
                    INSERT room_type (name, description, gallery)
                    VALUES (%s, %s, %s)
                """
      data_new = request.json
      name_new = data_new.get("name")
      description_new = data_new.get("description")
      gallery_new = data_new.get("gallery")
      if (not (name_new and description_new and gallery_new)):
        return jsonify({
            "status": "error",
            "message": "No se ingresaron los datos correctamente",
            }), 409
        #409 Conflict: El request no se pudo completar debido a un conflicto con el estado actual del recurso
      else:
        cur.execute(query,(name_new, description_new, gallery_new))
        conn.commit()
        return jsonify({
            "status": "success",
            "message": "Datos cargados con éxito",
            }),200


@room_types_bp.route('/room_types', methods=['GET', 'POST'])
def get_room_types():
    conn = None
    data = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if (request.method == 'POST'):
                get_room_types_post(conn,cur)
                cur.close()
            else:
                cur.execute('SELECT * FROM room_type ORDER BY id;')
                data = cur.fetchall()
                cur.close()
                if not data:
                    return jsonify({"status":"error","message":"Tabla 'room_type' vacía o no existe"}), 404
                return jsonify({"status":"success","message":"Datos de room_type obtenidos","data": data}), 200
    except Psycopg2Error as db_err:
        return jsonify({"status":"error","message":"Error DB al obtener room_types","error_details": str(db_err)}), 500
    finally:
        if conn:
            conn.close()