import os
from flask import Blueprint, send_from_directory, redirect

docs_bp = Blueprint('docs_bp', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWAGGER_UI_DIR = os.path.join(BASE_DIR, "swagger-ui")


@docs_bp.route("/docs/")
def swagger_ui():
    return send_from_directory(SWAGGER_UI_DIR, "index.html")


@docs_bp.route("/docs")
def swagger_ui_no_slash():
    # Redirigimos a la versión con barra
    return redirect("/docs/")


@docs_bp.route("/docs/<path:filename>")
def swagger_static(filename):
    return send_from_directory(SWAGGER_UI_DIR, filename)


@docs_bp.route("/swagger.yaml")
def swagger_spec():
    return send_from_directory(BASE_DIR, "swagger.yaml")