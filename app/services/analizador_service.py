"""Orquesta las fases del compilador: léxico → ER/AFND/AFD → sintáctico
(árbol) → semántico → traducción a SQL y JSON."""
from app.services.compilador import (lexico, automatas, graficos, jflap, sintactico,
                                      semantico, transpilador)


def compilar(codigo):
    tokens, errores_lexicos = lexico.analizar(codigo)

    # Tabla de tokens y lexemas (sin repetir lexemas)
    tabla_tokens, vistos = [], {}
    for t in tokens:
        clave = (t.tipo, t.lexema)
        if clave in vistos:
            vistos[clave]["apariciones"].append(f"{t.linea}:{t.columna}")
            continue
        er = automatas.er_de_token(t.tipo, t.lexema)[1] if t.tipo != "TK_ERROR" else "—"
        fila = {"token": t.tipo, "lexema": t.lexema, "er": er,
                "apariciones": [f"{t.linea}:{t.columna}"],
                "estado": "ERROR" if t.tipo == "TK_ERROR" else "OK", "detalle": t.detalle}
        vistos[clave] = fila
        tabla_tokens.append(fila)

    # ER, AFND y AFD de cada lexema (agrupados por expresión regular)
    lista_automatas = automatas.construir_automatas(tokens)
    for a in lista_automatas:
        a["afnd_svg"] = graficos.afnd_svg(a["afnd"])
        a["afd_svg"] = graficos.afd_svg(a["afd"])
        a["afnd_jff"] = jflap.afnd_jff(a["afnd"])
        a["afd_jff"] = jflap.afd_jff(a["afd"])

    # Análisis sintáctico y semántico regla por regla
    validos = [t for t in tokens if t.tipo != "TK_ERROR"]
    lineas = codigo.split("\n")
    fin = (len(lineas), len(lineas[-1]) + 1)
    reglas, errores_sint, errores_sem = [], [], []
    for n, toks in enumerate(sintactico.dividir_scripts(validos), 1):
        arbol, error = sintactico.analizar_script(toks, fin)
        info = {"n": n, "texto": " ".join(t.lexema for t in toks), "linea": toks[0].linea,
                "arbol_svg": None, "derivacion": [], "errores": [], "datos": None}
        if error:
            errores_sint.append(error)
            info["errores"].append(error)
        else:
            info["arbol_svg"] = graficos.arbol_svg(arbol)
            info["derivacion"] = sintactico.derivacion_izquierda(arbol)
            datos = semantico.extraer_regla(arbol)
            errs = semantico.analizar(datos, toks[0].linea)
            errores_sem += errs
            info["errores"] += errs
            info["datos"] = datos
        reglas.append(info)

    errores = errores_lexicos + errores_sint + errores_sem
    aprobado = bool(reglas) and not errores
    sql = json_txt = None
    if aprobado:  # RF05: solo se traduce si el lote está 100 % aprobado
        sql, json_txt = transpilador.traducir([r["datos"] for r in reglas])

    return {
        "codigo": codigo,
        "tabla_tokens": tabla_tokens,
        "total_tokens": len(tokens),
        "automatas": lista_automatas,
        "gramatica": sintactico.GRAMATICA,
        "terminales": sintactico.TERMINALES,
        "no_terminales": sintactico.NO_TERMINALES,
        "reglas": reglas,
        "errores": sorted(errores, key=lambda e: (e["linea"], e["columna"])),
        "aprobado": aprobado,
        "sql": sql,
        "json": json_txt,
        "alfabeto": lexico.ALFABETO_DESCRIPCION,
    }
