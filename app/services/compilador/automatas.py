"""Expresiones regulares, AFND (Thompson) y AFD (construcción de subconjuntos).

Los símbolos del alfabeto pueden ser caracteres sueltos ("S", "/", "=") o
clases disjuntas de caracteres ("a-z", "A-Z", "0-9"), igual que en las
expresiones regulares del documento.
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


def literal(palabra):
    return Cat(*[Sim(c) for c in palabra]) if len(palabra) > 1 else Sim(palabra)


def _rep(nodo_factory, veces):
    return [nodo_factory() for _ in range(veces)]


def er_de_token(tipo, lexema):
    """Devuelve (ast, notación formal, regex de Python) para un lexema."""
    if tipo in ("RESERVADA", "VARIABLE", "VALOR", "COMANDO", "OPERADOR_REL"):
        formal = lexema if len(lexema) == 1 else "·".join(lexema)
        return literal(lexema), formal, _escapar_py(lexema)
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
            a.trans.append((s, nodo.s, f))
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
    return (0 if s in CLASES else 1, s)


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
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return letras[i] if i < 26 else f"S{i}"


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
        "q0": afd.inicial,
        "F": "{" + ", ".join(afd.finales) + "}",
        "δ": "Q × Σ → Q (ver tabla de transiciones)",
    }


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
    return [f"δ({e}, {a}) = {afd.trans[(e, a)]}"
            for e in afd.estados for a in afd.alfabeto if (e, a) in afd.trans]


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
    """Agrupa los lexemas por su ER y construye AFND y AFD de cada una."""
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

    resultado = []
    for i, clave in enumerate(orden, 1):
        g = grupos[clave]
        afnd = thompson(g["ast"])
        afd_sub = subconjuntos(afnd)
        afd = minimizar(afd_sub)
        simbolos_afnd, filas_afnd = tabla_afnd(afnd)
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
            "tabla_sub": tabla_afd(afd_sub),
            "minimizado": len(afd.estados) < len(afd_sub.estados),
            "afd": afd,
            "quintupla": quintupla(afd),
            "tabla": tabla_afd(afd),
            "transiciones": lista_transiciones_afd(afd),
            "simulaciones": [
                {"lexema": lx, "aceptada": ok, "camino": " → ".join(cam)}
                for lx in g["lexemas"]
                for ok, cam in [simular(afd, lx)]
            ],
        })
    return resultado


# Tabla de ER por tipo de token (para mostrar la definición general)
ER_POR_TIPO = [
    ("RESERVADA", "SI | ENTONCES | Y | O | ACCION"),
    ("VARIABLE", "TIPO_LINEA | OPERADOR"),
    ("VALOR", "PREPAGO | POSTPAGO | MOV | CLA | ENT"),
    ("COMANDO", "RENOVAR | MIGRAR | SUSPENDER"),
    ("OPERADOR_REL", "== | != | > | < | >= | <="),
    ("NUMERO", "9 · (0-9)^8"),
    ("FECHA", "(0-9)^2 · / · (0-9)^2 · / · (0-9)^4"),
    ("TEXTO", "(a-z | A-Z | _) · (a-z | A-Z | 0-9 | _)*"),
]

assert {t for t, _ in ER_POR_TIPO} >= {c for c, _ in lexico.CATEGORIAS}
