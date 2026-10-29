# app/services/compilador/sintactico.py

def analizar_sintaxis(tokens):
    errores_sintacticos = []
    if not tokens:
        return ["No hay tokens para analizar sintácticamente."]

    t_tipos = [t['token'] for t in tokens if t['token'] != 'ERROR']
    
    if len(t_tipos) > 0:
        if t_tipos[0] != 'RESERVADA' or tokens[0]['lexema'] != 'SI':
            errores_sintacticos.append("Error sintáctico: La regla debe iniciar con la palabra reservada 'SI'.")
        
        if t_tipos[-1] != 'COMANDO':
            errores_sintacticos.append("Error sintáctico: La regla debe finalizar con un comando de acción (Ej: RENOVAR).")
            
        if 'ENTONCES' not in [t['lexema'] for t in tokens]:
            errores_sintacticos.append("Error sintáctico: Falta la palabra reservada 'ENTONCES'.")

    return errores_sintacticos