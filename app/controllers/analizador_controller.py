from flask import render_template, request
from app.services.analizador_service import analizar_texto

def procesar_analisis():
    texto_ingresado = ""
    tokens = []
    tokens_unicos = []
    
    if request.method == 'POST':
        archivo = request.files.get('archivo')
        if archivo and archivo.filename != '':
            texto_ingresado = archivo.read().decode('utf-8')
        else:
            texto_ingresado = request.form.get('texto', '')
        
        if texto_ingresado:
            tokens = analizar_texto(texto_ingresado)
            
            # DEDUPLICACIÓN: Extraemos lexemas únicos para generar las tarjetas visuales una sola vez
            lexemas_vistos = set()
            for t in tokens:
                if t['lexema'] not in lexemas_vistos:
                    lexemas_vistos.add(t['lexema'])
                    tokens_unicos.append(t)
            
    return render_template('index.html', tokens=tokens, tokens_unicos=tokens_unicos, texto_ingresado=texto_ingresado)