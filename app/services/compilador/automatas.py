"""Expresiones regulares, AFND (Thompson) y AFD (construcción de subconjuntos).

En la ER se usan rangos como (0-9) o (a-z), igual que en el documento, pero
en los autómatas cada rango se expande a sus caracteres explícitos
(0, 1, 2, ..., 9): cada transición lee un solo símbolo, como en JFLAP.
Los estados se nombran q0, q1, q2, ...
"""
from collections import deque

from . import lexico

EPS = "ε"
CLASES = {"a-z": ("a", "z"), "A-Z": ("A", "Z"), "0-9": ("0", "9")}


# ---------------------------------------------------------------- ER (AST)
class Sim:
    def __init__(self, s):
        self.s = s


class Cat:
    def __init__(self, *hijos):
        self.hijos = list(hijos)


class Alt:
    def __init__(self, *hijos):
        self.hijos = list(hijos)


class Estrella:
    def __init__(self, hijo):
        self.hijo = hijo


def expandir(simbolo):
    """Convierte un rango en la lista de sus caracteres: '0-9' → 0,1,...,9."""
    if simbolo in CLASES:
        lo, hi = CLASES[simbolo]
        return [chr(c) for c in range(ord(lo), ord(hi) + 1)]
    return [simbolo]


def literal(palabra):
    return Cat(*[Sim(c) for c in palabra]) if len(palabra) > 1 else Sim(palabra)


def _rep(nodo_factory, veces):
    return [nodo_factory() for _ in range(veces)]


# Palabras de cada token cuya ER es una unión de palabras fijas
PALABRAS_TOKEN = {
    "RESERVADA": lexico.RESERVADAS,
    "VARIABLE": lexico.VARIABLES,
    "VALOR_LINEA": lexico.VALORES_LINEA,
    "VALOR_OPERADOR": lexico.VALORES_OPERADOR,
    "COMANDO": lexico.COMANDOS,
    "OPERADOR_REL": lexico.OPERADORES_REL,
}
ORDEN_TOKENS = ["RESERVADA", "VARIABLE", "VALOR_LINEA", "VALOR_OPERADOR", "COMANDO",
                "OPERADOR_REL", "NUMERO", "FECHA", "TEXTO"]


def er_de_token(tipo, lexema=None):
    """Devuelve (ast, notación formal, regex de Python) de la ER del TOKEN.
    La ER es la misma para todos los lexemas del token (p. ej. VALOR_OPERADOR
    = MOV | CLA | ENT | BIT aunque en el script solo aparezca CLA)."""
    if tipo in PALABRAS_TOKEN:
        palabras = PALABRAS_TOKEN[tipo]
        ast = Alt(*[literal(p) for p in palabras])
        return ast, " | ".join(palabras), "|".join(_escapar_py(p) for p in palabras)
    if tipo == "NUMERO":
        ast = Cat(Sim("9"), *_rep(lambda: Sim("0-9"), 8))
        return ast, "9 · (0-9)^8", "9[0-9]{8}"
    if tipo == "FECHA":
        d = lambda: Sim("0-9")
        ast = Cat(d(), d(), Sim("/"), d(), d(), Sim("/"), d(), d(), d(), d())
        return ast, "(0-9)^2 · / · (0-9)^2 · / · (0-9)^4", "[0-9]{2}/[0-9]{2}/[0-9]{4}"
    if tipo == "TEXTO":
        ast = Cat(
            Alt(Sim("a-z"), Sim("A-Z"), Sim("_")),
            Estrella(Alt(Sim("a-z"), Sim("A-Z"), Sim("0-9"), Sim("_"))),
        )
        return ast, "(a-z | A-Z | _) · (a-z | A-Z | 0-9 | _)*", "[a-zA-Z_][a-zA-Z0-9_]*"
    return None, "", ""


def _escapar_py(s):
    import re
    return re.escape(s)


# ---------------------------------------------------------------- AFND
class AFND:
    def __init__(self):
        self.n = 0
        self.trans = []  # (origen, simbolo, destino)
        self.inicial = None
        self.final = None

    def nuevo(self):
        self.n += 1
        return self.n - 1


def thompson(ast):
    """Construcción de Thompson (Aho et al.): en la concatenación el estado
    final del primer fragmento se fusiona con el inicial del siguiente."""
    a = AFND()

    def construir(nodo, inicio=None):
        if isinstance(nodo, Sim):
            s = inicio if inicio is not None else a.nuevo()
            f = a.nuevo()
            for c in expandir(nodo.s):  # un rango (0-9) → 10 transiciones
                a.trans.append((s, c, f))
            return s, f
        if isinstance(nodo, Cat):
            s, f = construir(nodo.hijos[0], inicio)
            for h in nodo.hijos[1:]:
                _, f = construir(h, f)
            return s, f
        if isinstance(nodo, Alt):
            s = inicio if inicio is not None else a.nuevo()
            subs = [construir(h) for h in nodo.hijos]
            f = a.nuevo()
            for hs, hf in subs:
                a.trans.append((s, EPS, hs))
                a.trans.append((hf, EPS, f))
            return s, f
        if isinstance(nodo, Estrella):
            s = inicio if inicio is not None else a.nuevo()
            hs, hf = construir(nodo.hijo)
            f = a.nuevo()
            a.trans += [(s, EPS, hs), (hf, EPS, hs), (hf, EPS, f), (s, EPS, f)]
            return s, f
        raise ValueError("Nodo de ER desconocido")

    a.inicial, a.final = construir(ast)
    return _renumerar(a)


def _renumerar(a):
    """Renombra los estados q0..qn en orden de recorrido desde el inicial."""
    ady = {}
    for o, s, d in a.trans:
        ady.setdefault(o, []).append(d)
    orden, vistos, cola = [], {a.inicial}, deque([a.inicial])
    while cola:
        e = cola.popleft()
        orden.append(e)
        for d in ady.get(e, []):
            if d not in vistos:
                vistos.add(d)
                cola.append(d)
    mapa = {e: i for i, e in enumerate(orden)}
    b = AFND()
    b.n = len(orden)
    b.trans = [(mapa[o], s, mapa[d]) for o, s, d in a.trans]
    b.inicial, b.final = mapa[a.inicial], mapa[a.final]
    return b


def alfabeto(trans):
    simbolos = {s for _, s, _ in trans if s != EPS}
    return sorted(simbolos, key=_orden_simbolo)


def _orden_simbolo(s):
    # dígitos, mayúsculas, minúsculas y luego los demás símbolos
    if s.isdigit():
        return (0, s)
    if "A" <= s <= "Z":
        return (1, s)
    if "a" <= s <= "z":
        return (2, s)
    return (3, s)


# ---------------------------------------------------------------- AFD
class AFD:
    def __init__(self):
        self.estados = []  # nombres A, B, C...
        self.conjuntos = {}  # nombre -> frozenset de estados del AFND
        self.trans = {}  # (estado, simbolo) -> estado
        self.inicial = None
        self.finales = []
        self.alfabeto = []
        self.grupos = {}  # solo en el AFD mínimo: estado -> estados agrupados


def _nombre_estado(i):
    return f"q{i}"


def subconjuntos(afnd):
    eps = {}
    mov = {}
    for o, s, d in afnd.trans:
        if s == EPS:
            eps.setdefault(o, set()).add(d)
        else:
            mov.setdefault((o, s), set()).add(d)

    def cerradura(estados):
        pila, res = list(estados), set(estados)
        while pila:
            e = pila.pop()
            for d in eps.get(e, ()):
                if d not in res:
                    res.add(d)
                    pila.append(d)
        return frozenset(res)

    afd = AFD()
    afd.alfabeto = alfabeto(afnd.trans)
    inicio = cerradura({afnd.inicial})
    nombres = {inicio: _nombre_estado(0)}
    afd.estados.append(nombres[inicio])
    afd.conjuntos[nombres[inicio]] = inicio
    afd.inicial = nombres[inicio]
    pendientes = deque([inicio])
    while pendientes:
        T = pendientes.popleft()
        for a in afd.alfabeto:
            destino = set()
            for e in T:
                destino |= mov.get((e, a), set())
            if not destino:
                continue
            U = cerradura(destino)
            if U not in nombres:
                nombres[U] = _nombre_estado(len(nombres))
                afd.estados.append(nombres[U])
                afd.conjuntos[nombres[U]] = U
                pendientes.append(U)
            afd.trans[(nombres[T], a)] = nombres[U]
    afd.finales = [n for n in afd.estados if afnd.final in afd.conjuntos[n]]
    return afd


def minimizar(afd):
    """Minimización por refinamiento de particiones (algoritmo de Moore).
    Se usa un estado sumidero implícito para las transiciones indefinidas."""
    SUM = "∅"
    estados = afd.estados + [SUM]

    def delta(e, a):
        return SUM if e == SUM else afd.trans.get((e, a), SUM)

    bloque = {e: (1 if e in afd.finales else 0) for e in estados}
    while True:
        firmas = {}
        nuevo = {}
        for e in estados:
            firma = (bloque[e],) + tuple(bloque[delta(e, a)] for a in afd.alfabeto)
            nuevo[e] = firmas.setdefault(firma, len(firmas))
        if len(set(nuevo.values())) == len(set(bloque.values())):
            break
        bloque = nuevo
    muertos = {b for e, b in bloque.items() if e == SUM}

    # Renombrar los bloques útiles en orden de recorrido desde el inicial
    m = AFD()
    m.alfabeto = afd.alfabeto
    nombre = {}
    cola = deque([bloque[afd.inicial]])
    nombre[bloque[afd.inicial]] = _nombre_estado(0)
    while cola:
        b = cola.popleft()
        rep = next(e for e in afd.estados if bloque[e] == b)
        for a in afd.alfabeto:
            d = bloque[delta(rep, a)]
            if d in muertos:
                continue
            if d not in nombre:
                nombre[d] = _nombre_estado(len(nombre))
                cola.append(d)
            m.trans[(nombre[b], a)] = nombre[d]
    m.estados = list(nombre.values())
    m.inicial = nombre[bloque[afd.inicial]]
    m.grupos = {nombre[b]: [e for e in afd.estados if bloque[e] == b] for b in nombre}
    m.finales = [n for b, n in nombre.items() if m.grupos[n][0] in afd.finales]
    m.conjuntos = {}
    return m


def coincide(simbolo, c):
    if simbolo in CLASES:
        lo, hi = CLASES[simbolo]
        return lo <= c <= hi
    return simbolo == c


def simular(afd, cadena):
    """Recorre el AFD con la cadena. Devuelve (aceptada, camino)."""
    estado = afd.inicial
    camino = [estado]
    for c in cadena:
        siguiente = None
        for a in afd.alfabeto:
            if coincide(a, c) and (estado, a) in afd.trans:
                siguiente = afd.trans[(estado, a)]
                break
        if siguiente is None:
            return False, camino
        estado = siguiente
        camino.append(estado)
    return estado in afd.finales, camino


def quintupla(afd):
    return {
        "Q": "{" + ", ".join(afd.estados) + "}",
        "Σ": "{" + ", ".join(afd.alfabeto) + "}",
        "δ": "Q × Σ → Q (ver tabla y lista de transiciones)",
        "q0": afd.inicial,
        "F": "{" + ", ".join(afd.finales) + "}",
    }


def agrupar_columnas(simbolos, filas):
    """Para que la tabla quepa en pantalla, junta en una sola columna los
    símbolos que tienen exactamente las mismas transiciones (p. ej. 0, 1, ..., 9).
    Devuelve (encabezados, filas) con las celdas ya agrupadas."""
    grupos = []  # (simbolos, indice de columna representativa)
    for j, s in enumerate(simbolos):
        col = tuple(f["celdas"][j] for f in filas)
        for g in grupos:
            if g[1] == col and s != EPS and g[0][0] != EPS:
                g[0].append(s)
                break
        else:
            grupos.append(([s], col, j))
    encabezados = [", ".join(g[0]) for g in grupos]
    nuevas = [dict(f, celdas=[f["celdas"][g[2]] for g in grupos]) for f in filas]
    return encabezados, nuevas


def tabla_afd(afd):
    filas = []
    for e in afd.estados:
        marca = ("→ " if e == afd.inicial else "") + ("* " if e in afd.finales else "")
        if afd.conjuntos:
            origen = "{" + ", ".join(f"q{x}" for x in sorted(afd.conjuntos[e])) + "}"
        else:
            origen = "{" + ", ".join(afd.grupos[e]) + "}"
        filas.append({
            "estado": e,
            "marca": marca.strip(),
            "conjunto": origen,
            "celdas": [afd.trans.get((e, a), "∅") for a in afd.alfabeto],
        })
    return filas


def lista_transiciones_afd(afd):
    """δ(q, a) = p. Si varios símbolos van al mismo estado se escriben juntos."""
    lineas = []
    for e in afd.estados:
        por_destino = {}
        for a in afd.alfabeto:
            if (e, a) in afd.trans:
                por_destino.setdefault(afd.trans[(e, a)], []).append(a)
        for d, simbolos in por_destino.items():
            if len(simbolos) == 1:
                lineas.append(f"δ({e}, {simbolos[0]}) = {d}")
            else:
                lineas.append(f"δ({e}, x) = {d}   para x ∈ {{{', '.join(simbolos)}}}")
    return lineas


def tabla_afnd(afnd):
    simbolos = alfabeto(afnd.trans) + [EPS]
    filas = []
    for q in range(afnd.n):
        celdas = []
        for s in simbolos:
            dest = sorted(d for o, x, d in afnd.trans if o == q and x == s)
            celdas.append("{" + ", ".join(f"q{d}" for d in dest) + "}" if dest else "∅")
        marca = ("→ " if q == afnd.inicial else "") + ("* " if q == afnd.final else "")
        filas.append({"estado": f"q{q}", "marca": marca.strip(), "celdas": celdas})
    return simbolos, filas


# ---------------------------------------------------------------- Agrupación
def construir_automatas(tokens):
    """Construye la ER, el AFND y el AFD de cada TOKEN que aparece en el
    script, y verifica en el AFD cada lexema encontrado de ese token."""
    grupos, orden = {}, []
    for t in tokens:
        if t.tipo == "TK_ERROR":
            continue
        ast, formal, py = er_de_token(t.tipo, t.lexema)
        clave = (t.tipo, py)
        if clave not in grupos:
            grupos[clave] = {"tipo": t.tipo, "ast": ast, "formal": formal,
                             "python": py, "lexemas": []}
            orden.append(clave)
        if t.lexema not in grupos[clave]["lexemas"]:
            grupos[clave]["lexemas"].append(t.lexema)

    orden.sort(key=lambda c: ORDEN_TOKENS.index(c[0]))
    resultado = []
    for i, clave in enumerate(orden, 1):
        g = grupos[clave]
        afnd = thompson(g["ast"])
        afd_sub = subconjuntos(afnd)
        afd = minimizar(afd_sub)
        simbolos_afnd, filas_afnd = agrupar_columnas(*tabla_afnd(afnd))
        enc_sub, filas_sub = agrupar_columnas(afd_sub.alfabeto, tabla_afd(afd_sub))
        enc_min, filas_min = agrupar_columnas(afd.alfabeto, tabla_afd(afd))
        resultado.append({
            "id": i,
            "tipo": g["tipo"],
            "formal": g["formal"],
            "python": g["python"],
            "lexemas": g["lexemas"],
            "afnd": afnd,
            "afnd_simbolos": simbolos_afnd,
            "afnd_tabla": filas_afnd,
            "afd_sub": afd_sub,
            "tabla_sub": filas_sub,
            "tabla_sub_simbolos": enc_sub,
            "minimizado": len(afd.estados) < len(afd_sub.estados),
            "afd": afd,
            "quintupla": quintupla(afd),
            "tabla": filas_min,
            "tabla_simbolos": enc_min,
            "transiciones": lista_transiciones_afd(afd),
            "simulaciones": [
                {"lexema": lx, "aceptada": ok, "camino": " → ".join(cam)}
                for lx in g["lexemas"]
                for ok, cam in [simular(afd, lx)]
            ],
        })
    return resultado

