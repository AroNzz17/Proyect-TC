# app/routes.py
from flask import Blueprint, request
from app.controllers.analizador_controller import procesar_analisis

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    return procesar_analisis()