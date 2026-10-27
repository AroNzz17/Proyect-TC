import re

def obtener_teoria_automata(token_tipo, lexema):
    teoria = {
        'TK_TIPO_LINEA': {
            'er': '^(PRE|POS)$',
            'estados': 'q0 → qf',
            'quintupla': {'Q': '{q0, qf}', 'Sigma': '{P,R,E,O,S}', 'delta': 'δ', 'q0': 'q0', 'F': '{qf}'},
            'afn_mermaid': f'graph LR\n q0((q0)) -- ε --> q1((q1))\n q1 -- "{lexema}" --> qf(((qf)))',
            'afd_mermaid': f'graph LR\n q0((q0)) -- "{lexema}" --> qf(((qf)))'
        },
        'TK_SEPARADOR': {
            'er': '^\\|$',
            'estados': 'q0 → qf',
            'quintupla': {'Q': '{q0, qf}', 'Sigma': '{|}', 'delta': 'δ', 'q0': 'q0', 'F': '{qf}'},
            'afn_mermaid': f'graph LR\n q0((q0)) -- ε --> q1((q1))\n q1 -- "{lexema}" --> qf(((qf)))',
            'afd_mermaid': f'graph LR\n q0((q0)) -- "{lexema}" --> qf(((qf)))'
        },
        'TK_OPERADOR': {
            'er': '^(MOV|ENT|BIT)$',
            'estados': 'q0 → qf',
            'quintupla': {'Q': '{q0, qf}', 'Sigma': '{M,O,V,E,N,T,B,I}', 'delta': 'δ', 'q0': 'q0', 'F': '{qf}'},
            'afn_mermaid': f'graph LR\n q0((q0)) -- ε --> q1((q1))\n q1 -- "{lexema}" --> qf(((qf)))',
            'afd_mermaid': f'graph LR\n q0((q0)) -- "{lexema}" --> qf(((qf)))'
        },
        'TK_NUMERO': {
            'er': '^9[0-9]{8}$',
            'estados': 'q0 → qf',
            'quintupla': {'Q': '{q0, qf}', 'Sigma': '{0,1,2,3,4,5,6,7,8,9}', 'delta': 'δ', 'q0': 'q0', 'F': '{qf}'},
            'afn_mermaid': f'graph LR\n q0((q0)) -- ε --> q1((q1))\n q1 -- "{lexema}" --> qf(((qf)))',
            'afd_mermaid': f'graph LR\n q0((q0)) -- "{lexema}" --> qf(((qf)))'
        },
        'TK_FECHA': {
            'er': '^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/[0-9]{4}$',
            'estados': 'q0 → qf',
            'quintupla': {'Q': '{q0, qf}', 'Sigma': '{0,1,2,3,4,5,6,7,8,9,/}', 'delta': 'δ', 'q0': 'q0', 'F': '{qf}'},
            'afn_mermaid': f'graph LR\n q0((q0)) -- ε --> q1((q1))\n q1 -- "{lexema}" --> qf(((qf)))',
            'afd_mermaid': f'graph LR\n q0((q0)) -- "{lexema}" --> qf(((qf)))'
        }
    }
    
    if token_tipo == 'TK_ERROR':
        return {
             'er': 'Ninguna (No coincide con el alfabeto)',
             'estados': 'q0 → qError',
             'quintupla': {'Q': '{q0, qError}', 'Sigma': '{Σ_inválido}', 'delta': 'δ', 'q0': 'q0', 'F': '{qError}'},
             'afn_mermaid': f'graph LR\n q0((q0)) -- "{lexema}" --> qError(((Error)))',
             'afd_mermaid': f'graph LR\n q0((q0)) -- "{lexema}" --> qError(((Error)))'
        }

    return teoria.get(token_tipo, None)

def analizar_texto(texto):
    reglas = [
        ('TK_FECHA', r'(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/[0-9]{4}'),
        ('TK_NUMERO', r'9[0-9]{8}'),
        ('TK_OPERADOR', r'MOV|ENT|BIT'),
        ('TK_TIPO_LINEA', r'PRE|POS'),
        ('TK_SEPARADOR', r'\|'),
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