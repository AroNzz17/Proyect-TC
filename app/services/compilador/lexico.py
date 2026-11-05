# app/services/compilador/lexico.py
import re

def obtener_teoria_automata(token_tipo, lexema=""):
    
    if token_tipo == 'NUMERO':
        n = "0, 1, 2, 3, 4, 5, 6, 7, 8, 9"
        mermaid_graph = (
            f'graph LR\n'
            f'    q0((q0)) -- "9" --> q1((q1))\n'
            f'    q1 -- "{n}" --> q2((q2))\n'
            f'    q2 -- "{n}" --> q3((q3))\n'
            f'    q3 -- "{n}" --> q4((q4))\n'
            f'    q4 -- "{n}" --> q5((q5))\n'
            f'    q5 -- "{n}" --> q6((q6))\n'
            f'    q6 -- "{n}" --> q7((q7))\n'
            f'    q7 -- "{n}" --> q8((q8))\n'
            f'    q8 -- "{n}" --> q9(((q9)))'
        )
        return {
            'er': '9  (0-9)^8',
            'estados': 'Q = {q0, q1, q2, q3, q4, q5, q6, q7, q8, q9}',
            'quintupla': {
                'Q': '{q0..q9}', 
                'Sigma': '{0, 1, 2, 3, 4, 5, 6, 7, 8, 9}', 
                'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{q9}'
            },
            'afn_mermaid': mermaid_graph,
            'afd_mermaid': mermaid_graph
        }

    elif token_tipo == 'FECHA':
        n = "0, 1, 2, 3, 4, 5, 6, 7, 8, 9"
        mermaid_graph = (
            f'graph LR\n'
            f'    q0((q0)) -- "{n}" --> q1((q1))\n'
            f'    q1 -- "{n}" --> q2((q2))\n'
            f'    q2 -- "/" --> q3((q3))\n'
            f'    q3 -- "{n}" --> q4((q4))\n'
            f'    q4 -- "{n}" --> q5((q5))\n'
            f'    q5 -- "/" --> q6((q6))\n'
            f'    q6 -- "{n}" --> q7((q7))\n'
            f'    q7 -- "{n}" --> q8((q8))\n'
            f'    q8 -- "{n}" --> q9((q9))\n'
            f'    q9 -- "{n}" --> q10(((q10)))'
        )
        return {
            'er': '(0-9)^2  /  (0-9)^2  /  (0-9)^4',
            'estados': 'Q = {q0, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10}',
            'quintupla': {
                'Q': '{q0..q10}', 
                'Sigma': '{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, /}', 
                'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{q10}'
            },
            'afn_mermaid': mermaid_graph,
            'afd_mermaid': mermaid_graph
        }

    elif token_tipo == 'TEXTO':
        letras = "a, b, c, ..., z, A, B, C, ..., Z, _"
        letras_num = "a, b, c, ..., z, A, B, C, ..., Z, 0, 1, ..., 9, _"
        return {
            'er': '(a-z | A-Z | _)(a-z | A-Z | 0-9 | _)*',
            'estados': 'Q = {q0, q1, q2}',
            'quintupla': {
                'Q': '{q0, q1, q2}', 
                'Sigma': '{a..z, A..Z, 0..9, _}', 
                'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{q1}'
            },
            'afn_mermaid': (
                f'graph LR\n'
                f'    q0((q0)) -- "{letras}" --> q0\n'
                f'    q0 -- "ε" --> q1(((q1)))\n'
                f'    q1 -- "{letras_num}" --> q1'
            ),
            'afd_mermaid': (
                f'graph LR\n'
                f'    q0((q0)) -- "{letras}" --> q1(((q1)))\n'
                f'    q1 -- "{letras_num}" --> q1'
            )
        }

    elif token_tipo == 'RESERVADA':
        return {
            'er': 'SI | ENTONCES | Y | O | ACCION',
            'estados': 'Q = {q0..q13, qF}',
            'quintupla': {
                'Q': '{q0..q13, qF}', 'Sigma': '{S,I,E,N,T,O,C,A,Y}', 'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{qF}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> qS((qS)) -- "S" --> qI((qI)) -- "I" --> qF(((qF)))\n'
                '    q0 -- "ε" --> qY((qY)) -- "Y" --> qF\n'
                '    q0 -- "ε" --> qO((qO)) -- "O" --> qF\n'
                '    q0 -- "ε" --> qA((qA)) -- "A" --> qC1((qC1)) -- "C" --> qC2((qC2)) -- "C" --> qI2((qI2)) -- "I" --> qO2((qO2)) -- "O" --> qN((qN)) -- "N" --> qF\n'
                '    q0 -- "ε" --> qE((qE)) -- "E" --> qN2((qN2)) -- "N" --> qT((qT)) -- "T" --> qO3((qO3)) -- "O" --> qN3((qN3)) -- "N" --> qC3((qC3)) -- "C" --> qE2((qE2)) -- "E" --> qS2((qS2)) -- "S" --> qF'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "S" --> q1((q1)) -- "I" --> qF(((qF)))\n'
                '    q0 -- "Y" --> qF\n'
                '    q0 -- "O" --> qF\n'
                '    q0 -- "A" --> q2((q2)) -- "C" --> q3((q3)) -- "C" --> q4((q4)) -- "I" --> q5((q5)) -- "O" --> q6((q6)) -- "N" --> qF\n'
                '    q0 -- "E" --> q7((q7)) -- "N" --> q8((q8)) -- "T" --> q9((q9)) -- "O" --> q10((q10)) -- "N" --> q11((q11)) -- "C" --> q12((q12)) -- "E" --> q13((q13)) -- "S" --> qF'
            )
        }

    elif token_tipo == 'VARIABLE':
        return {
            'er': 'TIPO_LINEA | OPERADOR',
            'estados': 'Q = {q0..q16, qF}',
            'quintupla': {
                'Q': '{q0..q16, qF}', 'Sigma': '{T,I,P,O,_,L,N,E,A,R,D}', 'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{qF}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> qT((qT)) -- "T" --> qI((qI)) -- "I" --> qP((qP)) -- "P" --> qO((qO)) -- "O" --> q_((q_)) -- "_" --> qL((qL)) -- "L" --> qI2((qI2)) -- "I" --> qN((qN)) -- "N" --> qE((qE)) -- "E" --> qA((qA)) -- "A" --> qF(((qF)))\n'
                '    q0 -- "ε" --> qO1((qO1)) -- "O" --> qP1((qP1)) -- "P" --> qE1((qE1)) -- "E" --> qR1((qR1)) -- "R" --> qA1((qA1)) -- "A" --> qD1((qD1)) -- "D" --> qO2((qO2)) -- "O" --> qR2((qR2)) -- "R" --> qF'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "T" --> q1((q1)) -- "I" --> q2((q2)) -- "P" --> q3((q3)) -- "O" --> q4((q4)) -- "_" --> q5((q5)) -- "L" --> q6((q6)) -- "I" --> q7((q7)) -- "N" --> q8((q8)) -- "E" --> q9((q9)) -- "A" --> qF(((qF)))\n'
                '    q0 -- "O" --> q10((q10)) -- "P" --> q11((q11)) -- "E" --> q12((q12)) -- "R" --> q13((q13)) -- "A" --> q14((q14)) -- "D" --> q15((q15)) -- "O" --> q16((q16)) -- "R" --> qF'
            )
        }

    elif token_tipo == 'VALOR':
        return {
            'er': 'PREPAGO | POSTPAGO | MOV | CLA | ENT',
            'estados': 'Q = {q0..q15, qF}',
            'quintupla': {
                'Q': '{q0..q15, qF}', 'Sigma': '{P,R,E,A,G,O,S,T,M,V,C,L,N}', 'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{qF}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1)) -- "P" --> q2((q2)) -- "R" --> q3((q3)) -- "E" --> q4((q4)) -- "P" --> q5((q5)) -- "A" --> q6((q6)) -- "G" --> q7((q7)) -- "O" --> qF(((qF)))\n'
                '    q0 -- "ε" --> q8((q8)) -- "P" --> q9((q9)) -- "O" --> q10((q10)) -- "S" --> q11((q11)) -- "T" --> q12((q12)) -- "P" --> q13((q13)) -- "A" --> q14((q14)) -- "G" --> q15((q15)) -- "O" --> qF\n'
                '    q0 -- "ε" --> q16((q16)) -- "M" --> q17((q17)) -- "O" --> q18((q18)) -- "V" --> qF\n'
                '    q0 -- "ε" --> q19((q19)) -- "C" --> q20((q20)) -- "L" --> q21((q21)) -- "A" --> qF\n'
                '    q0 -- "ε" --> q22((q22)) -- "E" --> q23((q23)) -- "N" --> q24((q24)) -- "T" --> qF'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "P" --> q1((q1)) -- "R" --> q2((q2)) -- "E" --> q3((q3)) -- "P" --> q4((q4)) -- "A" --> q5((q5)) -- "G" --> q6((q6)) -- "O" --> qF(((qF)))\n'
                '    q1 -- "O" --> q7((q7)) -- "S" --> q8((q8)) -- "T" --> q9((q9)) -- "P" --> q4\n'
                '    q0 -- "M" --> q10((q10)) -- "O" --> q11((q11)) -- "V" --> qF\n'
                '    q0 -- "C" --> q12((q12)) -- "L" --> q13((q13)) -- "A" --> qF\n'
                '    q0 -- "E" --> q14((q14)) -- "N" --> q15((q15)) -- "T" --> qF'
            )
        }

    elif token_tipo == 'COMANDO':
        return {
            'er': 'RENOVAR | MIGRAR | SUSPENDER',
            'estados': 'Q = {q0..q19, qF}',
            'quintupla': {
                'Q': '{q0..q19, qF}', 'Sigma': '{R,E,N,O,V,A,M,I,G,S,U,P,D}', 'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{qF}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1)) -- "R" --> q2((q2)) -- "E" --> qF(((qF)))\n'
                '    q0 -- "ε" --> q3((q3)) -- "M" --> q4((q4)) -- "I" --> qF\n'
                '    q0 -- "ε" --> q5((q5)) -- "S" --> q6((q6)) -- "U" --> qF\n'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "R" --> q1((q1)) -- "E" --> q2((q2)) -- "N" --> q3((q3)) -- "O" --> q4((q4)) -- "V" --> q5((q5)) -- "A" --> q6((q6)) -- "R" --> qF(((qF)))\n'
                '    q0 -- "M" --> q7((q7)) -- "I" --> q8((q8)) -- "G" --> q9((q9)) -- "R" --> q10((q10)) -- "A" --> q11((q11)) -- "R" --> qF\n'
                '    q0 -- "S" --> q12((q12)) -- "U" --> q13((q13)) -- "S" --> q14((q14)) -- "P" --> q15((q15)) -- "E" --> q16((q16)) -- "N" --> q17((q17)) -- "D" --> q18((q18)) -- "E" --> q19((q19)) -- "R" --> qF'
            )
        }
        
    # 8. OPERADORES RELACIONALES
    elif token_tipo == 'OPERADOR_REL':
        return {
            'er': '== | != | >= | <= | > | <',
            'estados': 'Q = {q0, q1, q2, q3, q4, qF}',
            'quintupla': {
                'Q': '{q0..q4, qF}', 'Sigma': '{=, !, >, <}', 'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{qF}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1)) -- "=" --> q1_2((q1_2)) -- "=" --> qF(((qF)))\n'
                '    q0 -- "ε" --> q2((q2)) -- "!" --> q2_2((q2_2)) -- "=" --> qF\n'
                '    q0 -- "ε" --> q3((q3)) -- ">" --> qF\n'
                '    q0 -- "ε" --> q4((q4)) -- "<" --> qF\n'
                '    q3 -- "=" --> qF\n'
                '    q4 -- "=" --> qF'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "=" --> q1((q1)) -- "=" --> qF(((qF)))\n'
                '    q0 -- "!" --> q2((q2)) -- "=" --> qF\n'
                '    q0 -- ">" --> q3(((q3))) -- "=" --> qF\n'
                '    q0 -- "<" --> q4(((q4))) -- "=" --> qF'
            )
        }

    else:
        return {
            'er': 'ERROR',
            'estados': 'Q = {q0, q1}',
            'quintupla': {
                'Q': '{q0, q1}', 'Sigma': '{Caracteres}', 'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{q1}'
            },
            'afn_mermaid': 'graph LR\n    q0((q0)) -- "error" --> q1(((q1)))',
            'afd_mermaid': 'graph LR\n    q0((q0)) -- "error" --> q1(((q1)))'
        }

def analizar_texto(texto):
    reglas = [
        ('RESERVADA', r'\b(SI|ENTONCES|Y|O|ACCION)\b'),
        ('VARIABLE', r'\b(TIPO_LINEA|OPERADOR)\b'),
        ('VALOR', r'\b(PREPAGO|POSTPAGO|MOV|CLA|ENT)\b'),
        ('COMANDO', r'\b(RENOVAR|MIGRAR|SUSPENDER)\b'),
        ('OPERADOR_REL', r'==|!=|>=|<=|>|<'),
        ('FECHA', r'\b\d{2}/\d{2}/\d{4}\b'),               
        ('NUMERO', r'\b9\d{8}\b'),
        ('TEXTO', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),          
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
                    'linea': num_linea, 'lexema': lexema, 'token': tipo_token, 
                    'estado': estado, 'teoria': teoria
                })
                
    return tokens_encontrados