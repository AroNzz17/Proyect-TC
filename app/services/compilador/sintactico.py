def analizar_sintaxis(tokens):
    errores_sintacticos = []
    if not tokens:
        return ["No hay tokens para analizar sintácticamente."]

    # Filtramos estrictamente los tokens de la primera línea (la regla de negocio)
    tokens_primera_linea = [t for t in tokens if t['linea'] == 1 and t['token'] != 'ERROR']
    
    if not tokens_primera_linea:
        return ["Error sintáctico: No se encontró una regla válida en la primera línea."]

    t_tipos = [t['token'] for t in tokens_primera_linea]
    t_lexemas = [t['lexema'] for t in tokens_primera_linea]

    # 1. Validar que inicie con 'SI'
    if t_tipos[0] != 'RESERVADA' or t_lexemas[0] != 'SI':
        errores_sintacticos.append("Error sintáctico: La regla debe iniciar obligatoriamente con la palabra 'SI'.")
    
    # 2. Validar que contenga 'ENTONCES'
    if 'ENTONCES' not in t_lexemas:
        errores_sintacticos.append("Error sintáctico: Falta la palabra reservada 'ENTONCES'.")
        
    # 3. Validar que termine en un COMANDO
    if t_tipos[-1] != 'COMANDO':
        errores_sintacticos.append("Error sintáctico: La regla lógica debe finalizar con un comando de acción (Ej: RENOVAR, MIGRAR, SUSPENDER).")

    # 4. Validar estrictamente la estructura interna (VARIABLE seguida de OPERADOR_REL)
    for i in range(len(tokens_primera_linea)):
        if tokens_primera_linea[i]['token'] == 'VARIABLE':
            # Verificamos si hay un token siguiente y si es un operador relacional
            if i + 1 >= len(tokens_primera_linea) or tokens_primera_linea[i + 1]['token'] != 'OPERADOR_REL':
                variable_nombre = tokens_primera_linea[i]['lexema']
                errores_sintacticos.append(f"Error sintáctico: A la variable '{variable_nombre}' le falta un operador relacional (==, !=, >, <, >=, <=) a su derecha.")

    return errores_sintacticos