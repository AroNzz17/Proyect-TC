import re

def obtener_teoria_automata(token_tipo, lexema=""):
    
    if token_tipo == 'NUMERO':
        n = "0, 1, 2, 3, 4, 5, 6, 7, 8, 9"
        
        afn_graph = (
            f'graph LR\n'
            f'    q0((q0)) -- "ε" --> q1((q1))\n'
            f'    q1 -- "9" --> q2((q2))\n'
            f'    q2 -- "{n}" --> q3((q3))\n'
            f'    q3 -- "{n}" --> q4((q4))\n'
            f'    q4 -- "{n}" --> q5((q5))\n'
            f'    q5 -- "{n}" --> q6((q6))\n'
            f'    q6 -- "{n}" --> q7((q7))\n'
            f'    q7 -- "{n}" --> q8((q8))\n'
            f'    q8 -- "{n}" --> q9((q9))\n'
            f'    q9 -- "{n}" --> q10(((q10)))'
        )
        
        afd_graph = (
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
            'afn_mermaid': afn_graph,
            'afd_mermaid': afd_graph
        }

    elif token_tipo == 'FECHA':
        n = "0, 1, 2, 3, 4, 5, 6, 7, 8, 9"
        
        afn_graph = (
            f'graph LR\n'
            f'    q0((q0)) -- "ε" --> q1((q1))\n'
            f'    q1 -- "{n}" --> q2((q2))\n'
            f'    q2 -- "{n}" --> q3((q3))\n'
            f'    q3 -- "/" --> q4((q4))\n'
            f'    q4 -- "{n}" --> q5((q5))\n'
            f'    q5 -- "{n}" --> q6((q6))\n'
            f'    q6 -- "/" --> q7((q7))\n'
            f'    q7 -- "{n}" --> q8((q8))\n'
            f'    q8 -- "{n}" --> q9((q9))\n'
            f'    q9 -- "{n}" --> q10((q10))\n'
            f'    q10 -- "{n}" --> q11(((q11)))'
        )
        
        afd_graph = (
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
            'estados': 'Q = {q0..q10}',
            'quintupla': {
                'Q': '{q0..q10}', 
                'Sigma': '{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, /}', 
                'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{q10}'
            },
            'afn_mermaid': afn_graph,
            'afd_mermaid': afd_graph
        }

    elif token_tipo == 'TEXTO':
        letras = "a, b, c, ..., z, A, B, C, ..., Z, _"
        letras_num = "a, b, c, ..., z, A, B, C, ..., Z, 0, 1, ..., 9, _"
        return {
            'er': '(a-z | A-Z | _)(a-z | A-Z | 0-9 | _)*',
            'estados': 'Q = {q0, q1}',
            'quintupla': {
                'Q': '{q0, q1}', 
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
            'estados': 'Q = {q0..q14}',
            'quintupla': {
                'Q': '{q0..q14}', 'Sigma': '{S,I,E,N,T,O,C,A,Y}', 'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{q14}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1)) -- "S" --> q2((q2)) -- "I" --> q19(((q19)))\n'
                '    q0 -- "ε" --> q3((q3)) -- "Y" --> q19\n'
                '    q0 -- "ε" --> q4((q4)) -- "O" --> q19\n'
                '    q0 -- "ε" --> q5((q5)) -- "A" --> q6((q6)) -- "C" --> q7((q7)) -- "C" --> q8((q8)) -- "I" --> q9((q9)) -- "O" --> q10((q10)) -- "N" --> q19\n'
                '    q0 -- "ε" --> q11((q11)) -- "E" --> q12((q12)) -- "N" --> q13((q13)) -- "T" --> q14((q14)) -- "O" --> q15((q15)) -- "N" --> q16((q16)) -- "C" --> q17((q17)) -- "E" --> q18((q18)) -- "S" --> q19'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "S" --> q1((q1)) -- "I" --> q14(((q14)))\n'
                '    q0 -- "Y" --> q14\n'
                '    q0 -- "O" --> q14\n'
                '    q0 -- "A" --> q2((q2)) -- "C" --> q3((q3)) -- "C" --> q4((q4)) -- "I" --> q5((q5)) -- "O" --> q6((q6)) -- "N" --> q14\n'
                '    q0 -- "E" --> q7((q7)) -- "N" --> q8((q8)) -- "T" --> q9((q9)) -- "O" --> q10((q10)) -- "N" --> q11((q11)) -- "C" --> q12((q12)) -- "E" --> q13((q13)) -- "S" --> q14'
            )
        }

    elif token_tipo == 'VARIABLE':
        return {
            'er': 'TIPO_LINEA | OPERADOR',
            'estados': 'Q = {q0..q17}',
            'quintupla': {
                'Q': '{q0..q17}', 'Sigma': '{T,I,P,O,_,L,N,E,A,R,D}', 'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{q17}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1)) -- "T" --> q2((q2)) -- "I" --> q3((q3)) -- "P" --> q4((q4)) -- "O" --> q5((q5)) -- "_" --> q6((q6)) -- "L" --> q7((q7)) -- "I" --> q8((q8)) -- "N" --> q9((q9)) -- "E" --> q10((q10)) -- "A" --> q19(((q19)))\n'
                '    q0 -- "ε" --> q11((q11)) -- "O" --> q12((q12)) -- "P" --> q13((q13)) -- "E" --> q14((q14)) -- "R" --> q15((q15)) -- "A" --> q16((q16)) -- "D" --> q17((q17)) -- "O" --> q18((q18)) -- "R" --> q19'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "T" --> q1((q1)) -- "I" --> q2((q2)) -- "P" --> q3((q3)) -- "O" --> q4((q4)) -- "_" --> q5((q5)) -- "L" --> q6((q6)) -- "I" --> q7((q7)) -- "N" --> q8((q8)) -- "E" --> q9((q9)) -- "A" --> q17(((q17)))\n'
                '    q0 -- "O" --> q10((q10)) -- "P" --> q11((q11)) -- "E" --> q12((q12)) -- "R" --> q13((q13)) -- "A" --> q14((q14)) -- "D" --> q15((q15)) -- "O" --> q16((q16)) -- "R" --> q17'
            )
        }

    elif token_tipo == 'VALOR':
        return {
            'er': 'PREPAGO | POSTPAGO | MOV | CLA | ENT',
            'estados': 'Q = {q0..q16}',
            'quintupla': {
                'Q': '{q0..q16}', 'Sigma': '{P,R,E,A,G,O,S,T,M,V,C,L,N}', 'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{q16}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1)) -- "P" --> q2((q2)) -- "R" --> q3((q3)) -- "E" --> q4((q4)) -- "P" --> q5((q5)) -- "A" --> q6((q6)) -- "G" --> q7((q7)) -- "O" --> q25(((q25)))\n'
                '    q0 -- "ε" --> q8((q8)) -- "P" --> q9((q9)) -- "O" --> q10((q10)) -- "S" --> q11((q11)) -- "T" --> q12((q12)) -- "P" --> q13((q13)) -- "A" --> q14((q14)) -- "G" --> q15((q15)) -- "O" --> q25\n'
                '    q0 -- "ε" --> q16((q16)) -- "M" --> q17((q17)) -- "O" --> q18((q18)) -- "V" --> q25\n'
                '    q0 -- "ε" --> q19((q19)) -- "C" --> q20((q20)) -- "L" --> q21((q21)) -- "A" --> q25\n'
                '    q0 -- "ε" --> q22((q22)) -- "E" --> q23((q23)) -- "N" --> q24((q24)) -- "T" --> q25'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "P" --> q1((q1)) -- "R" --> q2((q2)) -- "E" --> q3((q3)) -- "P" --> q4((q4)) -- "A" --> q5((q5)) -- "G" --> q6((q6)) -- "O" --> q16(((q16)))\n'
                '    q1 -- "O" --> q7((q7)) -- "S" --> q8((q8)) -- "T" --> q9((q9)) -- "P" --> q4\n'
                '    q0 -- "M" --> q10((q10)) -- "O" --> q11((q11)) -- "V" --> q16\n'
                '    q0 -- "C" --> q12((q12)) -- "L" --> q13((q13)) -- "A" --> q16\n'
                '    q0 -- "E" --> q14((q14)) -- "N" --> q15((q15)) -- "T" --> q16'
            )
        }

    elif token_tipo == 'COMANDO':
        return {
            'er': 'RENOVAR | MIGRAR | SUSPENDER',
            'estados': 'Q = {q0..q20}',
            'quintupla': {
                'Q': '{q0..q20}', 'Sigma': '{R,E,N,O,V,A,M,I,G,S,U,P,D}', 'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{q20}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1)) -- "R" --> q2((q2)) -- "E" --> q3((q3)) -- "N" --> q4((q4)) -- "O" --> q5((q5)) -- "V" --> q6((q6)) -- "A" --> q7((q7)) -- "R" --> q23(((q23)))\n'
                '    q0 -- "ε" --> q8((q8)) -- "M" --> q9((q9)) -- "I" --> q10((q10)) -- "G" --> q11((q11)) -- "R" --> q12((q12)) -- "A" --> q13((q13)) -- "R" --> q23\n'
                '    q0 -- "ε" --> q14((q14)) -- "S" --> q15((q15)) -- "U" --> q16((q16)) -- "S" --> q17((q17)) -- "P" --> q18((q18)) -- "E" --> q19((q19)) -- "N" --> q20((q20)) -- "D" --> q21((q21)) -- "E" --> q22((q22)) -- "R" --> q23'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "R" --> q1((q1)) -- "E" --> q2((q2)) -- "N" --> q3((q3)) -- "O" --> q4((q4)) -- "V" --> q5((q5)) -- "A" --> q6((q6)) -- "R" --> q20(((q20)))\n'
                '    q0 -- "M" --> q7((q7)) -- "I" --> q8((q8)) -- "G" --> q9((q9)) -- "R" --> q10((q10)) -- "A" --> q11((q11)) -- "R" --> q20\n'
                '    q0 -- "S" --> q12((q12)) -- "U" --> q13((q13)) -- "S" --> q14((q14)) -- "P" --> q15((q15)) -- "E" --> q16((q16)) -- "N" --> q17((q17)) -- "D" --> q18((q18)) -- "E" --> q19((q19)) -- "R" --> q20'
            )
        }
        
    elif token_tipo == 'OPERADOR_REL':
        return {
            'er': '== | != | >= | <= | > | <',
            'estados': 'Q = {q0..q5}',
            'quintupla': {
                'Q': '{q0..q5}', 'Sigma': '{=, !, >, <}', 'delta': 'δ(q, c)', 'q0': 'q0', 'F': '{q5}'
            },
            'afn_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "ε" --> q1((q1)) -- "=" --> q2((q2)) -- "=" --> q7(((q7)))\n'
                '    q0 -- "ε" --> q3((q3)) -- "!" --> q4((q4)) -- "=" --> q7\n'
                '    q0 -- "ε" --> q5((q5)) -- ">" --> q7\n'
                '    q0 -- "ε" --> q6((q6)) -- "<" --> q7\n'
                '    q5 -- "=" --> q7\n'
                '    q6 -- "=" --> q7'
            ),
            'afd_mermaid': (
                'graph LR\n'
                '    q0((q0)) -- "=" --> q1((q1)) -- "=" --> q5(((q5)))\n'
                '    q0 -- "!" --> q2((q2)) -- "=" --> q5\n'
                '    q0 -- ">" --> q3(((q3))) -- "=" --> q5\n'
                '    q0 -- "<" --> q4(((q4))) -- "=" --> q5'
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