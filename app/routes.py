# app/routes.py
from flask import Blueprint
from app.controllers.analizador_controller import procesar_analisis, api_analizar

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    return procesar_analisis()


@main.route('/api/analizar', methods=['POST'])
def api():
    return api_analizar()
