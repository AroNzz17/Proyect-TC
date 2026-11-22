"""Traducción (transpilación) de las reglas validadas a SQL y JSON.

Esquema de base de datos supuesto en el servidor central:
  lineas(numero, tipo_linea, operador, estado)
  tramites_portabilidad(id, celular, accion, fecha_tramite, observacion, estado)
"""
import json

ESQUEMA_SQL = """-- Esquema asumido en el servidor central
CREATE TABLE IF NOT EXISTS lineas (
    numero      CHAR(9)     PRIMARY KEY,
    tipo_linea  VARCHAR(10) NOT NULL,   -- PREPAGO | POSTPAGO
    operador    VARCHAR(3)  NOT NULL,   -- MOV | CLA | ENT
    estado      VARCHAR(15) NOT NULL DEFAULT 'ACTIVA'
);
CREATE TABLE IF NOT EXISTS tramites_portabilidad (
    id             SERIAL       PRIMARY KEY,
    celular        CHAR(9)      NOT NULL REFERENCES lineas(numero),
    accion         VARCHAR(10)  NOT NULL,  -- RENOVAR | MIGRAR | SUSPENDER
    fecha_tramite  DATE         NOT NULL,
    observacion    VARCHAR(255),
    estado         VARCHAR(15)  NOT NULL DEFAULT 'PENDIENTE'
);
"""

COLUMNA = {"TIPO_LINEA": "tipo_linea", "OPERADOR": "operador"}
OP_SQL = {"==": "=", "!=": "<>", ">": ">", "<": "<", ">=": ">=", "<=": "<="}
CONECTOR_SQL = {"Y": "AND", "O": "OR"}


def _sql_texto(valor):
    return "'" + str(valor).replace("'", "''") + "'"


def _fecha_iso(ddmmyyyy):
    d, m, a = ddmmyyyy.split("/")
    return f"{a}-{m}-{d}"


def regla_a_sql(regla, n):
    condiciones = []
    for c in regla["condiciones"]:
        expr = f"l.{COLUMNA[c['variable']]} {OP_SQL[c['operador']]} {_sql_texto(c['valor'])}"
        if c["conector"]:
            expr = f"{CONECTOR_SQL[c['conector']]} {expr}"
        condiciones.append(expr)
    filtro = "(" + "\n       ".join(condiciones) + ")"

    meta = regla["metadatos"]
    celular = meta.get("CELULAR", {}).get("valor")
    fecha = meta.get("FECHA_TRAMITE", {}).get("valor")
    fecha_sql = _sql_texto(_fecha_iso(fecha)) if fecha else "CURRENT_DATE"
    obs_sql = _sql_texto(regla["comentario"]) if regla["comentario"] else "NULL"

    donde = []
    if celular:
        donde.append(f"l.numero = {_sql_texto(celular)}")
    donde.append(filtro)
    return (
        f"-- Regla {n}: SI ... ENTONCES ACCION {regla['accion']}\n"
        "INSERT INTO tramites_portabilidad (celular, accion, fecha_tramite, observacion, estado)\n"
        f"SELECT l.numero, {_sql_texto(regla['accion'])}, {fecha_sql}, {obs_sql}, 'PENDIENTE'\n"
        "FROM lineas l\n"
        "WHERE " + "\n  AND ".join(donde) + ";"
    )


def regla_a_dict(regla, n):
    meta = regla["metadatos"]
    fecha = meta.get("FECHA_TRAMITE", {}).get("valor")
    return {
        "regla": n,
        "condiciones": [
            {"conector": c["conector"], "variable": c["variable"],
             "operador": c["operador"], "valor": c["valor"]}
            for c in regla["condiciones"]
        ],
        "accion": regla["accion"],
        "metadatos": {
            "celular": meta.get("CELULAR", {}).get("valor"),
            "fecha_tramite": _fecha_iso(fecha) if fecha else None,
            "observacion": regla["comentario"] or None,
        },
        "estado": "APROBADA",
    }


def traducir(reglas):
    """reglas: lista de reglas ya validadas (sin errores)."""
    sql = ESQUEMA_SQL + "\n" + "\n\n".join(regla_a_sql(r, i) for i, r in enumerate(reglas, 1))
    datos = {"lote": [regla_a_dict(r, i) for i, r in enumerate(reglas, 1)],
             "total_reglas": len(reglas)}
    return sql, json.dumps(datos, ensure_ascii=False, indent=2)
