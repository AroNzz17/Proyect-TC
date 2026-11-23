"""Gráficos generados por código: se dibujan como SVG a partir de las
estructuras de datos (no son imágenes estáticas)."""
import itertools
import math
from collections import deque
from html import escape

R = 20  # radio de los estados
MARGEN = 60
_ids = itertools.count(1)


def _capas(estados, inicial, aristas):
    """Columna de cada estado = camino más largo desde el inicial, ignorando
    las aristas que cierran ciclos. Así las flechas siempre avanzan a la
    derecha y el estado final queda al extremo derecho."""
    ady = {}
    for o, _, d in aristas:
        if o != d and d not in ady.setdefault(o, []):
            ady[o].append(d)
    # 1) aristas de retorno (cierran un ciclo) mediante DFS
    retorno, color = set(), {}
    pila = [(inicial, iter(ady.get(inicial, [])))]
    color[inicial] = 1
    while pila:
        e, it = pila[-1]
        d = next(it, None)
        if d is None:
            color[e] = 2
            pila.pop()
        elif color.get(d) == 1:
            retorno.add((e, d))
        elif d not in color:
            color[d] = 1
            pila.append((d, iter(ady.get(d, []))))
    # 2) camino más largo en el grafo sin ciclos (orden topológico)
    entrantes = {e: 0 for e in estados}
    for o, ds in ady.items():
        for d in ds:
            if (o, d) not in retorno:
                entrantes[d] += 1
    nivel = {e: 0 for e in estados}
    cola = deque(e for e in estados if entrantes[e] == 0)
    while cola:
        e = cola.popleft()
        for d in ady.get(e, []):
            if (e, d) in retorno:
                continue
            nivel[d] = max(nivel[d], nivel[e] + 1)
            entrantes[d] -= 1
            if entrantes[d] == 0:
                cola.append(d)
    return nivel


def _por_linea(simbolos):
    """Símbolos por renglón: 5 para rangos cortos (0-9), 13 para letras (a..m)."""
    return 13 if len(simbolos) > 20 else 5


def _renglones(simbolos):
    n = _por_linea(simbolos)
    return [", ".join(simbolos[i:i + n]) for i in range(0, len(simbolos), n)]


def _medidas(simbolos):
    r = _renglones(simbolos)
    return 7.2 * max(len(x) for x in r) + 10, 15 * len(r) + 3


def _etiqueta(lx, ly, simbolos, modo):
    """Dibuja la etiqueta de una transición. Si tiene muchos símbolos
    (p. ej. 0, 1, ..., 9) se reparte en varios renglones, como en JFLAP.
    modo: 'arriba' (crece hacia arriba), 'abajo' o 'centro'."""
    renglones = _renglones(simbolos)
    ancho, alto = _medidas(simbolos)
    if modo == "arriba":
        top = ly + 7 - alto
    elif modo == "abajo":
        top = ly
    else:
        top = ly - alto / 2
    partes = [f'<rect x="{lx - ancho / 2:.1f}" y="{top:.1f}" width="{ancho:.1f}" '
              f'height="{alto:.1f}" rx="3" class="fondo-etq"/>']
    for k, r in enumerate(renglones):
        partes.append(f'<text x="{lx:.1f}" y="{top + 13 + 15 * k:.1f}" class="etq">{escape(r)}</text>')
    return "".join(partes), top, top + alto


def _filas(estados, inicial, agrupadas, nivel):
    """Fila de cada estado: cada estado intenta quedarse en la fila de su
    predecesor, así cada palabra (cadena de estados) ocupa su propia fila."""
    preds = {e: [] for e in estados}
    for (o, d) in agrupadas:
        if o != d and nivel[o] < nivel[d]:
            preds[d].append(o)
    indice = {e: k for k, e in enumerate(estados)}
    hijos = {e: [] for e in estados}
    for d, ps in preds.items():
        if len(ps) == 1:
            hijos[ps[0]].append(d)
    fila, ocupadas = {}, set()
    for e in sorted(estados, key=lambda x: (nivel[x], indice[x])):
        filas_p = sorted(fila[p] for p in preds[e] if p in fila)
        deseada = filas_p[(len(filas_p) - 1) // 2] if filas_p else 0
        if len(preds[e]) == 1:  # hermanos: uno debajo del otro, en orden
            hermanos = sorted(hijos[preds[e][0]], key=lambda x: indice[x])
            deseada += hermanos.index(e) - (len(hermanos) - 1) // 2
        k = 0
        while True:  # busca la fila libre más cercana: 0, +1, -1, +2, -2...
            f = deseada + ((k + 1) // 2 if k % 2 else -(k // 2))
            if (nivel[e], f) not in ocupadas:
                break
            k += 1
        fila[e] = f
        ocupadas.add((nivel[e], f))
    minimo = min(fila.values())
    return {e: f - minimo for e, f in fila.items()}


def automata_svg(estados, inicial, finales, aristas, etiqueta=str):
    """estados: lista; aristas: (origen, simbolo, destino)."""
    fid = f"flecha{next(_ids)}"  # id único: varias SVG conviven en la página
    nivel = _capas(estados, inicial, aristas)
    # Agrupa símbolos entre el mismo par de estados
    agrupadas = {}
    for o, s, d in aristas:
        agrupadas.setdefault((o, d), []).append(s)
    # La separación entre columnas se adapta al ancho de las etiquetas
    medidas = [_medidas(v) for v in agrupadas.values()] or [(0, 0)]
    DX = max(110, max(m[0] for m in medidas) + 40)
    DY = max(80, max(m[1] for m in medidas) + 50)
    fila = _filas(estados, inicial, agrupadas, nivel)
    ocupadas = {(nivel[e], fila[e]) for e in estados}
    pos = {e: (MARGEN + 30 + nivel[e] * DX, MARGEN + 80 + fila[e] * DY) for e in estados}

    def libre(f, c_desde, c_hasta):
        return all((c, f) not in ocupadas for c in range(c_desde, c_hasta + 1))

    ancho = MARGEN * 2 + 30 + (max(nivel.values()) + 1) * DX
    partes, etiquetas = [], []
    curva_n = 0
    ys = [y for _, y in pos.values()]
    for (o, d), simbolos in agrupadas.items():
        x1, y1 = pos[o]
        x2, y2 = pos[d]
        largo = len(_renglones(simbolos)) > 1
        if o == d:
            camino = (f"M {x1 - 8} {y1 - R + 2} C {x1 - 30} {y1 - 70}, "
                      f"{x1 + 30} {y1 - 70}, {x1 + 8} {y1 - R + 2}")
            lx, ly = x1, y1 - 66
            modo = "arriba"
            ys.append(y1 - 70)
        else:
            salto = nivel[d] - nivel[o]
            ruta = None  # lista de puntos por los que pasa la flecha
            if salto == 1 or (salto > 1 and fila[o] == fila[d] and libre(fila[o], nivel[o] + 1, nivel[d] - 1)):
                ruta = [(x1, y1), (x2, y2)]
            elif salto > 1 and libre(fila[o], nivel[o] + 1, nivel[d] - 1):
                # avanza por su propia fila y entra al destino en la última columna
                ruta = [(x1, y1), (x2 - DX, y1), (x2, y2)]
            elif salto > 1 and libre(fila[d], nivel[o] + 1, nivel[d] - 1):
                ruta = [(x1, y1), (x1 + DX, y2), (x2, y2)]
            elif salto > 1:
                # usa la fila libre más cercana (puede ser una nueva arriba o abajo)
                filas_usadas = [f for _, f in ocupadas]
                candidatas = range(min(filas_usadas) - 1, max(filas_usadas) + 2)
                libres = [f for f in candidatas if libre(f, nivel[o] + 1, nivel[d] - 1)]
                f = min(libres, key=lambda f: (abs(f - fila[o]), f))
                yr = MARGEN + 80 + f * DY
                ruta = [(x1, y1), (x1 + DX, yr), (x2 - DX, yr), (x2, y2)]
                ys.append(yr)
            if ruta:
                (ax, ay), (bx, by) = ruta[0], ruta[1]
                dist = math.hypot(bx - ax, by - ay)
                sx, sy = ax + (bx - ax) / dist * R, ay + (by - ay) / dist * R
                (cx_, cy_), (ex_, ey_) = ruta[-2], ruta[-1]
                dist = math.hypot(ex_ - cx_, ey_ - cy_)
                ex, ey = ex_ - (ex_ - cx_) / dist * R, ey_ - (ey_ - cy_) / dist * R
                puntos = [(sx, sy)] + ruta[1:-1] + [(ex, ey)]
                camino = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in puntos)
                # etiqueta sobre el tramo más largo
                tramos = list(zip(puntos, puntos[1:]))
                (px, py), (qx, qy) = max(tramos, key=lambda t: math.hypot(t[1][0] - t[0][0], t[1][1] - t[0][1]))
                lx, ly = (px + qx) / 2, (py + qy) / 2 - 7
                modo = "arriba"
                if largo:  # etiquetas largas: debajo de la flecha
                    ly, modo = (py + qy) / 2 + 6, "abajo"
            else:
                curva_n += 1
                hacia_atras = nivel[d] <= nivel[o]
                dist = math.hypot(x2 - x1, y2 - y1)
                altura = min(28 + dist * 0.22, 100) + (curva_n % 3) * 8
                cx = (x1 + x2) / 2
                if hacia_atras:   # las aristas de retorno se curvan por debajo
                    cy = max(y1, y2) + altura
                else:             # los demás saltos, por encima
                    cy = min(y1, y2) - altura
                a1 = math.atan2(cy - y1, cx - x1)
                a2 = math.atan2(cy - y2, cx - x2)
                sx, sy = x1 + R * math.cos(a1), y1 + R * math.sin(a1)
                ex, ey = x2 + R * math.cos(a2), y2 + R * math.sin(a2)
                camino = f"M {sx:.1f} {sy:.1f} Q {cx:.1f} {cy:.1f} {ex:.1f} {ey:.1f}"
                ys.append((y1 + y2) / 4 + cy / 2)
                lx = 0.25 * sx + 0.5 * cx + 0.25 * ex
                ly = 0.25 * sy + 0.5 * cy + 0.25 * ey
                modo = "centro" if hacia_atras else "arriba"
        partes.append(f'<path d="{camino}" class="arista" marker-end="url(#{fid})"/>')
        svg_etq, y_sup, y_inf = _etiqueta(lx, ly, simbolos, modo)
        etiquetas.append(svg_etq)
        ys += [y_sup + R, y_inf - R]

    partes += etiquetas  # las etiquetas van encima de las flechas
    x0, y0 = pos[inicial]
    partes.append(f'<path d="M {x0 - R - 34} {y0} L {x0 - R - 2} {y0}" class="arista" '
                  f'marker-end="url(#{fid})"/>')
    for e in estados:
        x, y = pos[e]
        partes.append(f'<circle cx="{x}" cy="{y}" r="{R}" class="estado"/>')
        if e in finales:
            partes.append(f'<circle cx="{x}" cy="{y}" r="{R - 4}" class="estado-final"/>')
        partes.append(f'<text x="{x}" y="{y + 4}" class="nombre">{escape(etiqueta(e))}</text>')

    y_min = min(ys) - R - 22
    alto = max(ys) + R + 22 - y_min
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" class="grafo" width="{ancho:.0f}" '
        f'height="{alto:.0f}" viewBox="0 {y_min:.0f} {ancho:.0f} {alto:.0f}">'
        f'<defs><marker id="{fid}" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" class="punta"/></marker></defs>'
        + "".join(partes) + "</svg>"
    )


def afnd_svg(afnd):
    return automata_svg(list(range(afnd.n)), afnd.inicial, [afnd.final], afnd.trans,
                        etiqueta=lambda q: f"q{q}")


def afd_svg(afd):
    aristas = [(o, s, d) for (o, s), d in afd.trans.items()]
    return automata_svg(afd.estados, afd.inicial, afd.finales, aristas)


# ---------------------------------------------------------------- Árbol
def arbol_svg(raiz):
    """Dibuja el árbol sintáctico: hojas en orden, padres centrados."""
    ANCHO_HOJA, ALTO_NIVEL = 104, 76
    nodos = []
    x_sig = [0]

    def ubicar(nodo, prof):
        hijos = nodo.get("hijos", [])
        if not hijos:
            x = x_sig[0]
            x_sig[0] += 1
        else:
            xs = [ubicar(h, prof + 1) for h in hijos]
            x = (xs[0] + xs[-1]) / 2
        nodo["_x"], nodo["_p"] = x, prof
        nodos.append(nodo)
        return x

    ubicar(raiz, 0)
    prof_max = max(n["_p"] for n in nodos)
    ancho = x_sig[0] * ANCHO_HOJA + 40
    alto = (prof_max + 1) * ALTO_NIVEL + 50

    def xy(n):
        return 20 + n["_x"] * ANCHO_HOJA + ANCHO_HOJA / 2, 34 + n["_p"] * ALTO_NIVEL

    partes = []
    for n in nodos:
        x, y = xy(n)
        for h in n.get("hijos", []):
            hx, hy = xy(h)
            partes.append(f'<line x1="{x:.1f}" y1="{y + 14}" x2="{hx:.1f}" y2="{hy - 16}" class="rama"/>')
    for n in nodos:
        x, y = xy(n)
        terminal = not n.get("hijos")
        etiqueta = n["etiqueta"]
        w = max(len(etiqueta), len(n.get("lexema", ""))) * 7.4 + 16
        h = 34 if terminal else 24
        clase = "hoja" if terminal else "interno"
        partes.append(f'<rect x="{x - w / 2:.1f}" y="{y - 14}" width="{w:.1f}" height="{h}" '
                      f'rx="6" class="{clase}"/>')
        partes.append(f'<text x="{x:.1f}" y="{y + 2}" class="t-{clase}">{escape(etiqueta)}</text>')
        if terminal:
            partes.append(f'<text x="{x:.1f}" y="{y + 15}" class="t-lexema">'
                          f'{escape(n.get("lexema", ""))}</text>')
        elif n.get("regla"):
            partes.append(f'<text x="{x + w / 2 + 4:.1f}" y="{y - 6}" class="t-regla">'
                          f'{escape(n["regla"])}</text>')
    for n in nodos:
        n.pop("_x", None)
        n.pop("_p", None)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" class="arbol" width="{ancho:.0f}" '
            f'height="{alto:.0f}" viewBox="0 0 {ancho:.0f} {alto:.0f}">' + "".join(partes) + "</svg>")
