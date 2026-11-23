"""Analizador léxico del DSL de reglas de portabilidad.

Recorre la entrada carácter por carácter (principio de la coincidencia más
larga) y produce la lista de tokens con su lexema, línea y columna.
"""
import re

RESERVADAS = ["SI", "ENTONCES", "Y", "O", "ACCION"]
VARIABLES = ["TIPO_LINEA", "OPERADOR"]
VALORES_LINEA = ["PREPAGO", "POSTPAGO"]          # tipos de línea
VALORES_OPERADOR = ["MOV", "CLA", "ENT", "BIT"]    # empresas operadoras
COMANDOS = ["RENOVAR", "MIGRAR", "SUSPENDER"]
OPERADORES_REL = ["==", "!=", ">", "<", ">=", "<="]

# Orden de prioridad cuando un identificador encaja en varias categorías:
# RESERVADA > VARIABLE > VALOR_LINEA > VALOR_OPERADOR > COMANDO > TEXTO
CATEGORIAS = [
    ("RESERVADA", RESERVADAS),
    ("VARIABLE", VARIABLES),
    ("VALOR_LINEA", VALORES_LINEA),
    ("VALOR_OPERADOR", VALORES_OPERADOR),
    ("COMANDO", COMANDOS),
]

RE_NUMERO = re.compile(r"9[0-9]{8}")
RE_FECHA = re.compile(r"[0-9]{2}/[0-9]{2}/[0-9]{4}")

ALFABETO_DESCRIPCION = (
    "Σ = {a-z, A-Z, 0-9, _, =, !, >, <, /, espacio, tabulación, salto de línea}"
)


class Token:
    __slots__ = ("tipo", "lexema", "linea", "columna", "detalle")

    def __init__(self, tipo, lexema, linea, columna, detalle=""):
        self.tipo = tipo
        self.lexema = lexema
        self.linea = linea
        self.columna = columna
        self.detalle = detalle

    def a_dict(self):
        return {
            "tipo": self.tipo,
            "lexema": self.lexema,
            "linea": self.linea,
            "columna": self.columna,
            "detalle": self.detalle,
        }

    def __repr__(self):
        return f"Token({self.tipo}, {self.lexema!r}, {self.linea}:{self.columna})"


def _es_letra(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_"


def _es_digito(c):
    return "0" <= c <= "9"


def clasificar_identificador(lexema):
    for tipo, palabras in CATEGORIAS:
        if lexema in palabras:
            return tipo
    return "TEXTO"


def analizar(texto):
    """Devuelve (tokens, errores). Los errores léxicos también se incluyen
    como tokens TK_ERROR para que aparezcan en la tabla de lexemas."""
    tokens, errores = [], []
    i, linea, col = 0, 1, 1
    n = len(texto)
    while i < n:
        c = texto[i]
        # Separadores: espacio, tabulación y salto de línea
        if c in " \t\r":
            i += 1
            col += 1
            continue
        if c == "\n":
            i += 1
            linea += 1
            col = 1
            continue

        inicio_col = col
        # Identificadores: (a-z | A-Z | _)(a-z | A-Z | 0-9 | _)*
        if _es_letra(c):
            j = i + 1
            while j < n and (_es_letra(texto[j]) or _es_digito(texto[j])):
                j += 1
            lexema = texto[i:j]
            tokens.append(Token(clasificar_identificador(lexema), lexema, linea, inicio_col))
            col += j - i
            i = j
            continue

        # Números y fechas: se lee el bloque completo de dígitos y '/'
        if _es_digito(c):
            j = i + 1
            while j < n and (_es_digito(texto[j]) or texto[j] == "/"):
                j += 1
            lexema = texto[i:j]
            if RE_FECHA.fullmatch(lexema):
                tokens.append(Token("FECHA", lexema, linea, inicio_col))
            elif RE_NUMERO.fullmatch(lexema):
                tokens.append(Token("NUMERO", lexema, linea, inicio_col))
            else:
                if "/" in lexema:
                    det = "Fecha mal formada: se esperaba DD/MM/YYYY"
                else:
                    det = "Número inválido: debe tener 9 dígitos y empezar con 9"
                t = Token("TK_ERROR", lexema, linea, inicio_col, det)
                tokens.append(t)
                errores.append(_error_lexico(t))
            col += j - i
            i = j
            continue

        # Operadores relacionales (primero los de dos caracteres)
        dos = texto[i:i + 2]
        if dos in ("==", "!=", ">=", "<="):
            tokens.append(Token("OPERADOR_REL", dos, linea, inicio_col))
            i += 2
            col += 2
            continue
        if c in "><":
            tokens.append(Token("OPERADOR_REL", c, linea, inicio_col))
            i += 1
            col += 1
            continue

        # Cualquier otro símbolo: fuera del alfabeto o mal usado
        if c in "=!":
            det = f"'{c}' solo es válido como parte de ==, != (falta un carácter)"
        elif c == "/":
            det = "'/' solo es válido dentro de una fecha DD/MM/YYYY"
        else:
            det = f"Símbolo '{c}' fuera del alfabeto del lenguaje"
        t = Token("TK_ERROR", c, linea, inicio_col, det)
        tokens.append(t)
        errores.append(_error_lexico(t))
        i += 1
        col += 1
    return tokens, errores


def _error_lexico(t):
    return {
        "fase": "Léxica",
        "linea": t.linea,
        "columna": t.columna,
        "mensaje": t.detalle,
        "lexema": t.lexema,
    }
