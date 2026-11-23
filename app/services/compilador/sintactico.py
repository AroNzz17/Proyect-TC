"""Analizador sintáctico descendente recursivo de la GLC del DSL.

Gramática (G = V, Σ, R, S) con S = <SCRIPT>:
  R1:  <SCRIPT>           → <REGLA> <BLOQUE_METADATOS>
  R2:  <SCRIPT>           → <REGLA>
  R3:  <REGLA>            → SI <CONDICION> ENTONCES ACCION <ACCION_FINAL>
  R4:  <CONDICION>        → VARIABLE OPERADOR_REL <VALOR>
  R5:  <CONDICION>        → VARIABLE OPERADOR_REL <VALOR> Y <CONDICION>
  R6:  <CONDICION>        → VARIABLE OPERADOR_REL <VALOR> O <CONDICION>
  R7:  <VALOR>            → VALOR_LINEA
  R8:  <VALOR>            → VALOR_OPERADOR
  R9:  <ACCION_FINAL>     → COMANDO
  R10: <BLOQUE_METADATOS> → <LINEA_INFO> <BLOQUE_METADATOS>
  R11: <BLOQUE_METADATOS> → <LINEA_INFO>
  R12: <LINEA_INFO>       → TEXTO FECHA
  R13: <LINEA_INFO>       → TEXTO NUMERO
  R14: <LINEA_INFO>       → <COMENTARIO>
  R15: <COMENTARIO>       → TEXTO <COMENTARIO>
  R16: <COMENTARIO>       → TEXTO

Para que el análisis sea determinista (sin ambigüedad), se mira un token por
delante: un TEXTO seguido de FECHA o NUMERO forma <LINEA_INFO> (R12/R13); en
cualquier otro caso el TEXTO inicia un <COMENTARIO>, que consume las palabras
siguientes hasta el final o hasta otro par TEXTO FECHA / TEXTO NUMERO.
"""

GRAMATICA = [
    ("R1", "<SCRIPT>", "<REGLA> <BLOQUE_METADATOS>"),
    ("R2", "<SCRIPT>", "<REGLA>"),
    ("R3", "<REGLA>", "SI <CONDICION> ENTONCES ACCION <ACCION_FINAL>"),
    ("R4", "<CONDICION>", "VARIABLE OPERADOR_REL <VALOR>"),
    ("R5", "<CONDICION>", "VARIABLE OPERADOR_REL <VALOR> Y <CONDICION>"),
    ("R6", "<CONDICION>", "VARIABLE OPERADOR_REL <VALOR> O <CONDICION>"),
    ("R7", "<VALOR>", "VALOR_LINEA"),
    ("R8", "<VALOR>", "VALOR_OPERADOR"),
    ("R9", "<ACCION_FINAL>", "COMANDO"),
    ("R10", "<BLOQUE_METADATOS>", "<LINEA_INFO> <BLOQUE_METADATOS>"),
    ("R11", "<BLOQUE_METADATOS>", "<LINEA_INFO>"),
    ("R12", "<LINEA_INFO>", "TEXTO FECHA"),
    ("R13", "<LINEA_INFO>", "TEXTO NUMERO"),
    ("R14", "<LINEA_INFO>", "<COMENTARIO>"),
    ("R15", "<COMENTARIO>", "TEXTO <COMENTARIO>"),
    ("R16", "<COMENTARIO>", "TEXTO"),
]
TERMINALES = ["SI", "ENTONCES", "Y", "O", "ACCION", "VARIABLE", "OPERADOR_REL",
              "VALOR_LINEA", "VALOR_OPERADOR", "COMANDO", "TEXTO", "NUMERO", "FECHA"]
NO_TERMINALES = ["<SCRIPT>", "<REGLA>", "<CONDICION>", "<VALOR>", "<ACCION_FINAL>",
                 "<BLOQUE_METADATOS>", "<LINEA_INFO>", "<COMENTARIO>"]


class ErrorSintactico(Exception):
    def __init__(self, mensaje, token):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.token = token


def _nombre(t):
    """Nombre del terminal tal como aparece en la gramática."""
    if t.tipo == "RESERVADA":
        return t.lexema
    return t.tipo


class Parser:
    def __init__(self, tokens, fin):
        self.t = tokens
        self.i = 0
        self.fin = fin  # (linea, columna) para errores al final de la entrada

    def actual(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def siguiente(self):
        return self.t[self.i + 1] if self.i + 1 < len(self.t) else None

    def esperar(self, esperado, descripcion=None):
        tok = self.actual()
        if tok is None or _nombre(tok) != esperado:
            desc = descripcion or esperado
            encontrado = "el fin de la regla" if tok is None else f"'{tok.lexema}' ({_nombre(tok)})"
            raise ErrorSintactico(f"Se esperaba {desc} pero se encontró {encontrado}", tok)
        self.i += 1
        return {"etiqueta": esperado, "lexema": tok.lexema}

    # <SCRIPT>
    def script(self):
        regla = self.regla()
        if self.actual() is None:
            return {"etiqueta": "<SCRIPT>", "regla": "R2", "hijos": [regla]}
        meta = self.bloque_metadatos()
        return {"etiqueta": "<SCRIPT>", "regla": "R1", "hijos": [regla, meta]}

    # <REGLA>
    def regla(self):
        hijos = [self.esperar("SI", "la palabra reservada SI al inicio de la regla")]
        hijos.append(self.condicion())
        hijos.append(self.esperar("ENTONCES", "la palabra reservada ENTONCES (o el conector Y / O)"))
        hijos.append(self.esperar("ACCION", "la palabra reservada ACCION después de ENTONCES"))
        hijos.append(self.accion_final())
        return {"etiqueta": "<REGLA>", "regla": "R3", "hijos": hijos}

    # <CONDICION>
    def condicion(self):
        hijos = [
            self.esperar("VARIABLE", "una VARIABLE (TIPO_LINEA u OPERADOR)"),
            self.esperar("OPERADOR_REL", "un OPERADOR_REL (==, !=, >, <, >=, <=)"),
            self.valor(),
        ]
        tok = self.actual()
        if tok is not None and _nombre(tok) in ("Y", "O"):
            conector = _nombre(tok)
            hijos.append(self.esperar(conector))
            hijos.append(self.condicion())
            return {"etiqueta": "<CONDICION>", "regla": "R5" if conector == "Y" else "R6",
                    "hijos": hijos}
        return {"etiqueta": "<CONDICION>", "regla": "R4", "hijos": hijos}

    # <VALOR>
    def valor(self):
        tok = self.actual()
        if tok is not None and _nombre(tok) == "VALOR_LINEA":
            return {"etiqueta": "<VALOR>", "regla": "R7", "hijos": [self.esperar("VALOR_LINEA")]}
        if tok is not None and _nombre(tok) == "VALOR_OPERADOR":
            return {"etiqueta": "<VALOR>", "regla": "R8", "hijos": [self.esperar("VALOR_OPERADOR")]}
        self.esperar("VALOR_LINEA", "un VALOR_LINEA (PREPAGO, POSTPAGO) o un "
                     "VALOR_OPERADOR (MOV, CLA, ENT, BIT)")

    # <ACCION_FINAL>
    def accion_final(self):
        return {"etiqueta": "<ACCION_FINAL>", "regla": "R9",
                "hijos": [self.esperar("COMANDO", "un COMANDO (RENOVAR, MIGRAR, SUSPENDER)")]}

    # <BLOQUE_METADATOS>
    def bloque_metadatos(self):
        linea = self.linea_info()
        if self.actual() is None:
            return {"etiqueta": "<BLOQUE_METADATOS>", "regla": "R11", "hijos": [linea]}
        resto = self.bloque_metadatos()
        return {"etiqueta": "<BLOQUE_METADATOS>", "regla": "R10", "hijos": [linea, resto]}

    def _es_par_dato(self):
        a, b = self.actual(), self.siguiente()
        return (a is not None and b is not None and _nombre(a) == "TEXTO"
                and _nombre(b) in ("FECHA", "NUMERO"))

    # <LINEA_INFO>
    def linea_info(self):
        if self._es_par_dato():
            clave = self.esperar("TEXTO")
            tipo = _nombre(self.actual())
            valor = self.esperar(tipo)
            return {"etiqueta": "<LINEA_INFO>", "regla": "R12" if tipo == "FECHA" else "R13",
                    "hijos": [clave, valor]}
        return {"etiqueta": "<LINEA_INFO>", "regla": "R14", "hijos": [self.comentario()]}

    # <COMENTARIO>
    def comentario(self):
        palabra = self.esperar("TEXTO", "un TEXTO (metadato o comentario)")
        tok = self.actual()
        if tok is not None and _nombre(tok) == "TEXTO" and not self._es_par_dato():
            return {"etiqueta": "<COMENTARIO>", "regla": "R15",
                    "hijos": [palabra, self.comentario()]}
        return {"etiqueta": "<COMENTARIO>", "regla": "R16", "hijos": [palabra]}


def dividir_scripts(tokens):
    """Un lote puede tener varias reglas: cada una empieza con SI."""
    scripts, actual = [], []
    for t in tokens:
        if t.tipo == "RESERVADA" and t.lexema == "SI" and actual:
            scripts.append(actual)
            actual = []
        actual.append(t)
    if actual:
        scripts.append(actual)
    return scripts


def analizar_script(tokens, fin):
    """Devuelve (arbol, error). error es None si la regla es válida."""
    p = Parser(tokens, fin)
    try:
        arbol = p.script()
        if p.actual() is not None:
            tok = p.actual()
            raise ErrorSintactico(f"Token inesperado '{tok.lexema}' ({_nombre(tok)}) "
                                  "después del final de la regla", tok)
        return arbol, None
    except ErrorSintactico as e:
        tok = e.token
        linea, col = (tok.linea, tok.columna) if tok is not None else fin
        return None, {"fase": "Sintáctica", "linea": linea, "columna": col,
                      "mensaje": e.mensaje, "lexema": tok.lexema if tok else ""}


def derivacion_izquierda(arbol):
    """Lista de formas sentenciales de la derivación por la izquierda."""
    pasos = []
    forma = [arbol]

    def texto(f):
        return " ".join(n["etiqueta"] if n.get("hijos") else n["etiqueta"] for n in f)

    pasos.append(texto(forma))
    while True:
        idx = next((k for k, n in enumerate(forma) if n.get("hijos")), None)
        if idx is None:
            break
        nodo = forma[idx]
        forma = forma[:idx] + nodo["hijos"] + forma[idx + 1:]
        pasos.append(f"⇒[{nodo['regla']}] " + texto(forma))
    return pasos
