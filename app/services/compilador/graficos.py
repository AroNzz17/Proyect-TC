"""Gráficos generados por código: se dibujan como SVG a partir de las
estructuras de datos (no son imágenes estáticas)."""
import itertools
import math
from collections import deque
from html import escape

R = 20  # radio de los estados
DX, DY = 120, 80
MARGEN = 60
_ids = itertools.count(1)


def _capas(estados, inicial, aristas):
    ady = {}
    for o, _, d in aristas:
        ady.setdefault(o, []).append(d)
    nivel = {inicial: 0}
    cola = deque([inicial])
    while cola:
        e = cola.popleft()
        for d in ady.get(e, []):
            if d not in nivel:
                nivel[d] = nivel[e] + 1
                cola.append(d)
    for e in estados:
        nivel.setdefault(e, max(nivel.values(), default=0) + 1)
    return nivel


def automata_svg(estados, inicial, finales, aristas, etiqueta=str):
    """estados: lista; aristas: (origen, simbolo, destino)."""
    fid = f"flecha{next(_ids)}"  # id único: varias SVG conviven en la página
    nivel = _capas(estados, inicial, aristas)
    columnas = {}
    for e in estados:
        columnas.setdefault(nivel[e], []).append(e)
    max_filas = max(len(v) for v in columnas.values())
    pos = {}
    for c, lista in columnas.items():
        desplaz = (max_filas - len(lista)) * DY / 2
        for f, e in enumerate(lista):
            pos[e] = (MARGEN + 30 + c * DX, MARGEN + 80 + desplaz + f * DY)

    # Agrupa símbolos entre el mismo par de estados
    agrupadas = {}
    for o, s, d in aristas:
        agrupadas.setdefault((o, d), []).append(s)

    ancho = MARGEN * 2 + 30 + (max(nivel.values()) + 1) * DX
    partes = []
    curva_n = 0
    ys = [y for _, y in pos.values()]
    for (o, d), simbolos in agrupadas.items():
        texto = escape(", ".join(simbolos))
        x1, y1 = pos[o]
        x2, y2 = pos[d]
        if o == d:
            camino = (f"M {x1 - 8} {y1 - R + 2} C {x1 - 30} {y1 - 70}, "
                      f"{x1 + 30} {y1 - 70}, {x1 + 8} {y1 - R + 2}")
            lx, ly = x1, y1 - 58
            ys.append(y1 - 70)
        else:
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            recta = (nivel[d] == nivel[o] + 1) and abs(dy) < 1 and (d, o) not in agrupadas
            if recta:
                ux, uy = dx / dist, dy / dist
                sx, sy = x1 + ux * R, y1 + uy * R
                ex, ey = x2 - ux * R, y2 - uy * R
                camino = f"M {sx:.1f} {sy:.1f} L {ex:.1f} {ey:.1f}"
                lx, ly = (sx + ex) / 2, (sy + ey) / 2 - 7
            else:
                curva_n += 1
                hacia_atras = nivel[d] <= nivel[o]
                altura = min(28 + dist * 0.22, 100) + (curva_n % 3) * 8
                cx = (x1 + x2) / 2
                if hacia_atras:   # las aristas de retorno se curvan por debajo
                    cy = max(y1, y2) + altura
                else:             # los saltos hacia adelante, por encima
                    cy = min(y1, y2) - altura
                a1 = math.atan2(cy - y1, cx - x1)
                a2 = math.atan2(cy - y2, cx - x2)
                sx, sy = x1 + R * math.cos(a1), y1 + R * math.sin(a1)
                ex, ey = x2 + R * math.cos(a2), y2 + R * math.sin(a2)
                camino = f"M {sx:.1f} {sy:.1f} Q {cx:.1f} {cy:.1f} {ex:.1f} {ey:.1f}"
                ys.append((y1 + y2) / 4 + cy / 2)
                lx = 0.25 * sx + 0.5 * cx + 0.25 * ex
                ly = 0.25 * sy + 0.5 * cy + 0.25 * ey
        partes.append(f'<path d="{camino}" class="arista" marker-end="url(#{fid})"/>')
        ancho_t = 7.2 * len(", ".join(simbolos)) + 8
        partes.append(
            f'<rect x="{lx - ancho_t / 2:.1f}" y="{ly - 10:.1f}" width="{ancho_t:.1f}" '
            f'height="16" rx="3" class="fondo-etq"/>'
            f'<text x="{lx:.1f}" y="{ly + 2:.1f}" class="etq">{texto}</text>')

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
