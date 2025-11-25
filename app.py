from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)

# Habilitar CORS para todas las rutas.
# Esto permite que el frontend en el puerto 5000 le hable al backend en el 5001.
CORS(app, resources={r"/*": {"origins": "*"}})

from routes.home import home_bp
from routes.rooms import rooms_bp
from routes.room_types import room_types_bp
from routes.availability import availability_bp
from routes.activities import activities_bp
from routes.services import services_bp
from routes.packages import packages_bp
from routes.reservations import reservations_bp

# Registrar Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(rooms_bp)
app.register_blueprint(room_types_bp)
app.register_blueprint(availability_bp)
app.register_blueprint(activities_bp)
app.register_blueprint(services_bp)
app.register_blueprint(packages_bp)
app.register_blueprint(reservations_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
