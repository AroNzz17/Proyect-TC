"""Exporta los autómatas al formato .jff de JFLAP (autómata finito).

Cada transición lee un solo símbolo y las transiciones vacías (ε) se
escriben como <read/>, que JFLAP muestra como λ (o ε según su configuración).
"""
from xml.sax.saxutils import escape

from .automatas import EPS
from .graficos import _capas

DX, DY = 130, 100


def a_jff(estados, inicial, finales, aristas, nombre=str):
    nivel = _capas(estados, inicial, aristas)
    filas = {}
    lineas = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
              '<!--Generado por el Compilador DSL de reglas de portabilidad.-->',
              "<structure>", "\t<type>fa</type>", "\t<automaton>"]
    ids = {}
    for i, e in enumerate(estados):
        ids[e] = i
        f = filas.get(nivel[e], 0)
        filas[nivel[e]] = f + 1
        lineas.append(f'\t\t<state id="{i}" name="{escape(nombre(e))}">')
        lineas.append(f"\t\t\t<x>{60 + nivel[e] * DX:.1f}</x>")
        lineas.append(f"\t\t\t<y>{80 + f * DY:.1f}</y>")
        if e == inicial:
            lineas.append("\t\t\t<initial/>")
        if e in finales:
            lineas.append("\t\t\t<final/>")
        lineas.append("\t\t</state>")
    for o, s, d in aristas:
        lineas.append("\t\t<transition>")
        lineas.append(f"\t\t\t<from>{ids[o]}</from>")
        lineas.append(f"\t\t\t<to>{ids[d]}</to>")
        lineas.append("\t\t\t<read/>" if s == EPS else f"\t\t\t<read>{escape(s)}</read>")
        lineas.append("\t\t</transition>")
    lineas += ["\t</automaton>", "</structure>"]
    return "\n".join(lineas) + "\n"


def afnd_jff(afnd):
    return a_jff(list(range(afnd.n)), afnd.inicial, [afnd.final], afnd.trans,
                 nombre=lambda q: f"q{q}")


def afd_jff(afd):
    aristas = [(o, s, d) for (o, s), d in afd.trans.items()]
    return a_jff(afd.estados, afd.inicial, afd.finales, aristas)
