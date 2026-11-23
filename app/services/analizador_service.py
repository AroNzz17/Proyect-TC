"""Orquesta las fases del compilador: léxico → ER/AFND/AFD → sintáctico
(árbol) → semántico → traducción a SQL y JSON."""
from app.services.compilador import (lexico, automatas, graficos, jflap, sintactico,
                                      semantico, transpilador)


def compilar(codigo):
    tokens, errores_lexicos = lexico.analizar(codigo)

    # Tabla de tokens: una fila por token, con sus lexemas y una sola ER
    filas = {}
    for t in tokens:
        if t.tipo not in filas:
            er = automatas.er_de_token(t.tipo)[1] if t.tipo != "TK_ERROR" else "—"
            filas[t.tipo] = {"token": t.tipo, "er": er, "lexemas": [], "lineas": [],
                             "estado": "ERROR" if t.tipo == "TK_ERROR" else "OK",
                             "detalles": []}
        f = filas[t.tipo]
        if t.lexema not in f["lexemas"] or t.tipo == "TK_ERROR":
            f["lexemas"].append(t.lexema)
        if t.linea not in f["lineas"]:
            f["lineas"].append(t.linea)
        if t.tipo == "TK_ERROR":
            f["detalles"].append(f"{t.linea}:{t.columna} '{t.lexema}': {t.detalle}")
    orden = automatas.ORDEN_TOKENS + ["TK_ERROR"]
    tabla_tokens = sorted(filas.values(), key=lambda f: orden.index(f["token"]))
    total_lexemas = len({(t.tipo, t.lexema) for t in tokens})

    # ER, AFND y AFD de cada token
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
        "total_lexemas": total_lexemas,
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
