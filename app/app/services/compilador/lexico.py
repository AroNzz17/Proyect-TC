# app/services/compilador/lexico.py
import re

def obtener_teoria_automata(token_tipo, lexema):
    """
    Genera el AFN, AFD y la Quíntupla exacta.
    La notación de ER utiliza llaves {...} para agrupar las opciones del lenguaje
    y los estados finales mantienen una numeración secuencial (ej. q6).
    """
    
    if token_tipo == 'RESERVADA':
        return {
            'er': '{SI | ENTONCES | Y | O | ACCION}',
            'estados': 'Q = {q0, q1, q2, q3, q4, q5, q6}',
            'quintupla': {
                'Q': '{q0, q1, q2, q3, q4, q5, q6}',
                'Sigma': '{S, I, E, N, T, O, C, A, Y}',
                'delta': 'δ(q, c)',
                'q0': 'q0',
                'F': '{q6}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1))\n'
                '    q0 -- "ε" --> q2((q2))\n'
                '    q0 -- "ε" --> q3((q3))\n'
                '    q0 -- "ε" --> q4((q4))\n'
                '    q0 -- "ε" --> q5((q5))\n'
                '    q1 -- "SI" --> q6(((q6)))\n'
                '    q2 -- "ENTONCES" --> q6\n'
                '    q3 -- "Y" --> q6\n'
                '    q4 -- "O" --> q6\n'
                '    q5 -- "ACCION" --> q6'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "SI" --> q6(((q6)))\n'
                '    q0 -- "ENTONCES" --> q6\n'
                '    q0 -- "Y" --> q6\n'
                '    q0 -- "O" --> q6\n'
                '    q0 -- "ACCION" --> q6'
            )
        }
        
    elif token_tipo == 'VARIABLE':
        return {
            'er': '{TIPO_LINEA | OPERADOR}',
            'estados': 'Q = {q0, q1, q2, q3}',
            'quintupla': {
                'Q': '{q0, q1, q2, q3}',
                'Sigma': '{T, I, P, O, _, L, N, E, A, R, D}',
                'delta': 'δ(q, c)',
                'q0': 'q0',
                'F': '{q3}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1))\n'
                '    q0 -- "ε" --> q2((q2))\n'
                '    q1 -- "TIPO_LINEA" --> q3(((q3)))\n'
                '    q2 -- "OPERADOR" --> q3'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "TIPO_LINEA" --> q3(((q3)))\n'
                '    q0 -- "OPERADOR" --> q3'
            )
        }
        
    elif token_tipo == 'VALOR':
        return {
            'er': '{PREPAGO | POSTPAGO | MOV | CLA | ENT}',
            'estados': 'Q = {q0, q1, q2, q3, q4, q5, q6}',
            'quintupla': {
                'Q': '{q0, q1, q2, q3, q4, q5, q6}',
                'Sigma': '{P, R, E, A, G, O, S, T, M, V, C, L, N}',
                'delta': 'δ(q, c)',
                'q0': 'q0',
                'F': '{q6}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1))\n'
                '    q0 -- "ε" --> q2((q2))\n'
                '    q0 -- "ε" --> q3((q3))\n'
                '    q0 -- "ε" --> q4((q4))\n'
                '    q0 -- "ε" --> q5((q5))\n'
                '    q1 -- "PREPAGO" --> q6(((q6)))\n'
                '    q2 -- "POSTPAGO" --> q6\n'
                '    q3 -- "MOV" --> q6\n'
                '    q4 -- "CLA" --> q6\n'
                '    q5 -- "ENT" --> q6'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "PREPAGO" --> q6(((q6)))\n'
                '    q0 -- "POSTPAGO" --> q6\n'
                '    q0 -- "MOV" --> q6\n'
                '    q0 -- "CLA" --> q6\n'
                '    q0 -- "ENT" --> q6'
            )
        }
        
    elif token_tipo == 'COMANDO':
        return {
            'er': '{RENOVAR | MIGRAR | SUSPENDER}',
            'estados': 'Q = {q0, q1, q2, q3, q4}',
            'quintupla': {
                'Q': '{q0, q1, q2, q3, q4}',
                'Sigma': '{R, E, N, O, V, A, M, I, G, S, U, P, D}',
                'delta': 'δ(q, c)',
                'q0': 'q0',
                'F': '{q4}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1))\n'
                '    q0 -- "ε" --> q2((q2))\n'
                '    q0 -- "ε" --> q3((q3))\n'
                '    q1 -- "RENOVAR" --> q4(((q4)))\n'
                '    q2 -- "MIGRAR" --> q4\n'
                '    q3 -- "SUSPENDER" --> q4'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "RENOVAR" --> q4(((q4)))\n'
                '    q0 -- "MIGRAR" --> q4\n'
                '    q0 -- "SUSPENDER" --> q4'
            )
        }
        
    elif token_tipo == 'OPERADOR_REL':
        return {
            'er': '{== | != | > | < | >= | <=}',
            'estados': 'Q = {q0, q1, q2, q3, q4, q5, q6, q7}',
            'quintupla': {
                'Q': '{q0, q1, q2, q3, q4, q5, q6, q7}',
                'Sigma': '{=, !, >, <}',
                'delta': 'δ(q, c)',
                'q0': 'q0',
                'F': '{q7}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1))\n'
                '    q0 -- "ε" --> q2((q2))\n'
                '    q0 -- "ε" --> q3((q3))\n'
                '    q0 -- "ε" --> q4((q4))\n'
                '    q0 -- "ε" --> q5((q5))\n'
                '    q0 -- "ε" --> q6((q6))\n'
                '    q1 -- "==" --> q7(((q7)))\n'
                '    q2 -- "!=" --> q7\n'
                '    q3 -- ">" --> q7\n'
                '    q4 -- "<" --> q7\n'
                '    q5 -- ">=" --> q7\n'
                '    q6 -- "<=" --> q7'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "==" --> q7(((q7)))\n'
                '    q0 -- "!=" --> q7\n'
                '    q0 -- ">" --> q7\n'
                '    q0 -- "<" --> q7\n'
                '    q0 -- ">=" --> q7\n'
                '    q0 -- "<=" --> q7'
            )
        }
        
    else:  # TK_ERROR
        return {
             'er': '{^Σ}*',
             'estados': 'Q = {q0, q1}',
             'quintupla': {
                 'Q': '{q0, q1}', 
                 'Sigma': '{Caracteres_No_Validos}', 
                 'delta': 'δ(q0, c) = q1', 
                 'q0': 'q0', 
                 'F': '{q1}'
             },
             'afn_mermaid': f'graph LR\n    q0((q0)) -- "{lexema}" --> q1(((q1)))',
             'afd_mermaid': f'graph LR\n    q0((q0)) -- "{lexema}" --> q1(((q1)))'
        }

def token_type_is_error(token_tipo):
    return token_tipo == 'TK_ERROR'

def analizar_texto(texto):
    reglas = [
        ('RESERVADA', r'\b(SI|ENTONCES|Y|O|ACCION)\b'),
        ('VARIABLE', r'\b(TIPO_LINEA|OPERADOR)\b'),
        ('VALOR', r'\b(PREPAGO|POSTPAGO|MOV|CLA|ENT)\b'),
        ('COMANDO', r'\b(RENOVAR|MIGRAR|SUSPENDER)\b'),
        ('OPERADOR_REL', r'==|!=|>|<|>=|<='),
        ('TK_ESPACIO', r'[ \t\r]+'), 
        ('TK_ERROR', r'.')
    ]
    patron_compilado = '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in reglas)
    regex = re.compile(patron_compilado)
    
    tokens_encontrados = []
    lineas = texto.split('\n')
    
    for num_linea, linea in enumerate(lineas, 1):
        if not linea.strip(): 
            continue
            
        for match in regex.finditer(linea):
            tipo_token = match.lastgroup
            lexema = match.group(tipo_token)
            
            if tipo_token != 'TK_ESPACIO':
                estado = "ERROR" if tipo_token == 'TK_ERROR' else "OK"
                teoria = obtener_teoria_automata(tipo_token, lexema)
                
                tokens_encontrados.append({
                    'linea': num_linea,
                    'lexema': lexema,
                    'token': tipo_token,
                    'estado': estado,
                    'teoria': teoria
                })
                
    return tokens_encontrados