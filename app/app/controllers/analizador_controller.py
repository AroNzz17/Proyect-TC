# app/controllers/analizador_controller.py
from flask import render_template, request
from app.services.compilador.lexico import analizar_texto
from app.services.compilador.sintactico import analizar_sintaxis
from app.services.compilador.semantico import analizar_semantica

def procesar_analisis():
    codigo_ingresado = ""
    tokens = []
    tokens_unicos = []
    
    if request.method == 'POST':
        # Si envían un archivo .txt o texto desde el textarea
        if 'archivo' in request.files and request.files['archivo'].filename != '':
            archivo = request.files['archivo']
            codigo_ingresado = archivo.read().decode('utf-8')
        else:
            codigo_ingresado = request.form.get('texto', '')
            
        if not codigo_ingresado:
            codigo_ingresado = request.form.get('codigo_fuente', '')

        if codigo_ingresado:
            tokens = analizar_texto(codigo_ingresado)
            
            # Filtrar tokens únicos para mostrar sus autómatas y quíntuplas sin repetir
            vistos = set()
            for t in tokens:
                if t['lexema'] not in vistos and t['estado'] == 'OK':
                    vistos.add(t['lexema'])
                    tokens_unicos.append(t)

    return render_template('index.html', 
                           codigo_ingresado=codigo_ingresado, 
                           tokens=tokens, 
                           tokens_unicos=tokens_unicos)