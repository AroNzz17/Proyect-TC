from flask import render_template, request, jsonify
from app.services.analizador_service import compilar

EJEMPLO = (
    "SI TIPO_LINEA == PREPAGO Y OPERADOR == CLA ENTONCES ACCION SUSPENDER\n"
    "FECHA_TRAMITE 03/11/2026\n"
    "CELULAR 989654321\n"
    "OBSERVACION Cliente solicito la suspension temporal del servicio"
)


def _leer_entrada():
    archivo = request.files.get('archivo')
    if archivo and archivo.filename:
        return archivo.read().decode('utf-8', errors='replace'), archivo.filename
    return request.form.get('texto', ''), None


def procesar_analisis():
    resultado = None
    codigo = EJEMPLO
    nombre_archivo = None
    if request.method == 'POST':
        codigo, nombre_archivo = _leer_entrada()
        codigo = codigo.replace('\r\n', '\n')
        if codigo.strip():
            resultado = compilar(codigo)
    return render_template('index.html', codigo_ingresado=codigo, resultado=resultado,
                           nombre_archivo=nombre_archivo, ejemplo=EJEMPLO)


def api_analizar():
    """Devuelve la traducción en JSON (útil para integrarlo con otros sistemas)."""
    datos = request.get_json(silent=True) or {}
    codigo = datos.get('codigo') or request.form.get('texto', '')
    r = compilar(codigo)
    return jsonify({
        'aprobado': r['aprobado'],
        'tokens': r['tabla_tokens'],
        'errores': r['errores'],
        'sql': r['sql'],
        'json': r['json'],
    })
