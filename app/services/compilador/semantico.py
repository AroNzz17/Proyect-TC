"""Análisis semántico: coherencia de tipos y valores sobre el árbol válido."""
from datetime import date

# Qué token de valor corresponde a cada variable
DOMINIO = {
    "TIPO_LINEA": "VALOR_LINEA",     # PREPAGO | POSTPAGO
    "OPERADOR": "VALOR_OPERADOR",    # MOV | CLA | ENT | BIT
}
EJEMPLOS = {"VALOR_LINEA": "PREPAGO, POSTPAGO", "VALOR_OPERADOR": "MOV, CLA, ENT, BIT"}
OPERADORES_PERMITIDOS = {"==", "!="}  # las variables son categóricas
METADATOS = {
    "FECHA_TRAMITE": "FECHA",
    "CELULAR": "NUMERO",
}


def _hojas(nodo):
    if not nodo.get("hijos"):
        return [nodo]
    res = []
    for h in nodo["hijos"]:
        res += _hojas(h)
    return res


def _buscar(nodo, etiqueta):
    if nodo["etiqueta"] == etiqueta:
        yield nodo
    for h in nodo.get("hijos") or []:
        yield from _buscar(h, etiqueta)


def extraer_regla(arbol):
    """Convierte el árbol en una estructura de datos de la regla."""
    regla = {"condiciones": [], "accion": None, "metadatos": {}, "comentario": ""}
    cond = next(_buscar(arbol, "<CONDICION>"))
    conector = None
    while cond is not None:
        h = cond["hijos"]
        valor = h[2]["hijos"][0]  # <VALOR> → VALOR_LINEA | VALOR_OPERADOR
        regla["condiciones"].append({
            "conector": conector,
            "variable": h[0]["lexema"],
            "operador": h[1]["lexema"],
            "valor": valor["lexema"],
            "tipo_valor": valor["etiqueta"],
        })
        if len(h) > 3:
            conector = h[3]["etiqueta"]
            cond = h[4]
        else:
            cond = None
    regla["accion"] = next(_buscar(arbol, "<ACCION_FINAL>"))["hijos"][0]["lexema"]
    palabras = []
    for linea in _buscar(arbol, "<LINEA_INFO>"):
        if linea["regla"] in ("R12", "R13"):
            clave, valor = linea["hijos"]
            regla["metadatos"][clave["lexema"]] = {"tipo": valor["etiqueta"],
                                                   "valor": valor["lexema"]}
        else:
            palabras += [h["lexema"] for h in _hojas(linea)]
    if palabras and palabras[0] == "OBSERVACION":
        palabras = palabras[1:]
    regla["comentario"] = " ".join(palabras)
    return regla


def analizar(regla, linea_regla):
    """Devuelve la lista de errores semánticos de una regla."""
    errores = []

    def error(msg):
        errores.append({"fase": "Semántica", "linea": linea_regla, "columna": 1,
                        "mensaje": msg, "lexema": ""})

    vistos = {}
    for c in regla["condiciones"]:
        var, op, val = c["variable"], c["operador"], c["valor"]
        esperado = DOMINIO[var]
        if c["tipo_valor"] != esperado:
            error(f"Incompatibilidad de tipos: {var} solo se compara con un {esperado} "
                  f"({EJEMPLOS[esperado]}), pero {val} es un {c['tipo_valor']}")
        if op not in OPERADORES_PERMITIDOS:
            error(f"El operador '{op}' no tiene sentido para {var}: es una variable "
                  "categórica, use == o !=")
        if op == "==" and c["conector"] != "O" and var in vistos and vistos[var] != val:
            error(f"Condición contradictoria: {var} no puede ser {vistos[var]} y {val} "
                  "a la vez")
        if op == "==":
            vistos.setdefault(var, val)

    for clave, dato in regla["metadatos"].items():
        esperado = METADATOS.get(clave)
        if esperado is None:
            error(f"Metadato desconocido '{clave}': use FECHA_TRAMITE o CELULAR")
        elif esperado != dato["tipo"]:
            error(f"El metadato {clave} debe ir seguido de un {esperado}, "
                  f"no de un {dato['tipo']}")
        if dato["tipo"] == "FECHA":
            d, m, a = (int(x) for x in dato["valor"].split("/"))
            try:
                date(a, m, d)
            except ValueError:
                error(f"La fecha {dato['valor']} no existe en el calendario")
    return errores
