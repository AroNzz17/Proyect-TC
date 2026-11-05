from flask import render_template, request
from app.services.compilador.lexico import analizar_texto
# NUEVO: Importar el analizador sintáctico
from app.services.compilador.sintactico import analizar_sintaxis

def procesar_analisis():
    codigo_ingresado = ""
    tokens = []
    tokens_agrupados = [] 
    categorias_unicas = []
    errores_sintacticos = [] # NUEVO: Inicializar la lista de errores
    
    if request.method == 'POST':
        if 'archivo' in request.files and request.files['archivo'].filename != '':
            archivo = request.files['archivo']
            codigo_ingresado = archivo.read().decode('utf-8')
        else:
            codigo_ingresado = request.form.get('texto', '')
            
        if not codigo_ingresado:
            codigo_ingresado = request.form.get('codigo_fuente', '')

        if codigo_ingresado:
            tokens = analizar_texto(codigo_ingresado)
            
            # NUEVO: Ejecutar el analizador sintáctico enviándole los tokens
            errores_sintacticos = analizar_sintaxis(tokens)
            
            # Agrupar lexemas por Token para la tabla 
            diccionario_agrupado = {}
            for t in tokens:
                tipo = t['token']
                lexema = t['lexema']
                
                if tipo not in diccionario_agrupado:
                    diccionario_agrupado[tipo] = {
                        'lineas': [t['linea']], 
                        'token': tipo,
                        'lexemas': {lexema}, 
                        'teoria': t['teoria'],
                        'estado': t['estado']
                    }
                else:
                    diccionario_agrupado[tipo]['lineas'].append(t['linea'])
                    diccionario_agrupado[tipo]['lexemas'].add(lexema)
            
            for tipo, datos in diccionario_agrupado.items():
                lineas_unicas = sorted(list(set(datos['lineas'])))
                lineas_str = ", ".join(map(str, lineas_unicas))
                lexemas_str = ", ".join(datos['lexemas'])
                
                tokens_agrupados.append({
                    'lineas': lineas_str,
                    'token': datos['token'],
                    'lexemas': lexemas_str,
                    'teoria': datos['teoria'],
                    'estado': datos['estado']
                })
            
            # Filtrar por TIPO DE TOKEN para mostrar la teoría del autómata maestro
            vistos_tokens = set()
            for t in tokens:
                if t['token'] not in vistos_tokens and t['estado'] == 'OK':
                    vistos_tokens.add(t['token'])
                    categorias_unicas.append(t)

    # NUEVO: Agregar la variable errores_sintacticos al render_template
    return render_template('index.html', 
                           codigo_ingresado=codigo_ingresado, 
                           tokens_agrupados=tokens_agrupados, 
                           categorias_unicas=categorias_unicas,
                           errores_sintacticos=errores_sintacticos)