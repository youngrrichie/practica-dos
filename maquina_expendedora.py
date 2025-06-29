import ply.lex as lex
import ply.yacc as yacc
import sys
import json

# Definición de tokens (analizador léxico)
tokens = (
    'DOLLAR',    # $
    'REFRESCO',  # R
    'DEVOLVER',  # <
    'LBRACE',    # {
    'RBRACE',    # }
)

# Expresiones regulares para tokens simples
t_DOLLAR = r'\$'
t_REFRESCO = r'R'
t_DEVOLVER = r'<'
t_LBRACE = r'\{'
t_RBRACE = r'\}'

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Manejo de saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores
def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)

# Crear el analizador léxico
lexer = lex.lex()

# Definición de reglas gramaticales (analizador sintáctico)

# P → { C }
def p_programa(p):
    'programa : LBRACE contenido RBRACE'
    # Atributos: valido, errores, saldo, refrescos, nivel, árbol
    contenido_valido, contenido_errores, contenido_saldo, contenido_refrescos, contenido_nivel, contenido_arbol = p[2]
    
    # El programa es válido si su contenido es válido y no hay errores
    valido = contenido_valido and len(contenido_errores) == 0
    
    # Construir árbol de derivación
    arbol = {
        'tipo': 'programa',
        'texto': '{ C }',
        'hijos': [contenido_arbol],
        'atributos': {
            'valido': valido,
            'saldo': contenido_saldo,
            'refrescos': contenido_refrescos,
            'nivel': 0,
            'errores': contenido_errores
        }
    }
    
    p[0] = (valido, contenido_errores, contenido_saldo, contenido_refrescos, 0, arbol)

# C → A C | ε
def p_contenido_con_accion(p):
    'contenido : accion contenido'
    # Extraer atributos de la acción
    accion_valido, accion_errores, accion_saldo, accion_refrescos, accion_nivel, accion_arbol = p[1]
    
    # Extraer atributos del contenido
    cont_valido, cont_errores, cont_saldo_resto, cont_refrescos_resto, cont_nivel, cont_arbol = p[2]
    
    # El nivel es el máximo entre ambos
    nivel_actual = max(accion_nivel, cont_nivel)
    
    # CORRECCIÓN: Simplificar la lógica - no validar restricciones aquí
    # Solo acumular los cambios de saldo y refrescos
    saldo_final = accion_saldo + cont_saldo_resto
    refrescos_total = accion_refrescos + cont_refrescos_resto
    
    # Combinar errores sin agregar validaciones adicionales
    errores_final = accion_errores.copy() + cont_errores.copy()
    
    # La validez depende de todos los componentes
    valido_final = accion_valido and cont_valido
    
    # Construir árbol de derivación
    arbol = {
        'tipo': 'contenido',
        'texto': 'A C',
        'hijos': [accion_arbol, cont_arbol],
        'atributos': {
            'valido': valido_final,
            'saldo': saldo_final,
            'refrescos': refrescos_total,
            'nivel': nivel_actual,
            'errores': errores_final
        }
    }
    
    p[0] = (valido_final, errores_final, saldo_final, refrescos_total, nivel_actual, arbol)

def p_contenido_vacio(p):
    'contenido : empty'
    # Para el contenido vacío, todos los valores son iniciales/neutrales
    arbol = {
        'tipo': 'contenido',
        'texto': 'ε',
        'hijos': [],
        'atributos': {
            'valido': True,
            'saldo': 0,
            'refrescos': 0,
            'nivel': 0,
            'errores': []
        }
    }
    p[0] = (True, [], 0, 0, 0, arbol)

# A → $ | R | < | { C }
def p_accion_dollar(p):
    'accion : DOLLAR'
    # Insertar moneda incrementa el saldo en 1
    arbol = {
        'tipo': 'accion',
        'texto': '$',
        'hijos': [],
        'atributos': {
            'valido': True,
            'saldo': 1,
            'refrescos': 0,
            'nivel': 0,
            'errores': []
        }
    }
    p[0] = (True, [], 1, 0, 0, arbol)

def p_accion_refresco(p):
    'accion : REFRESCO'
    # Un refresco cuesta 3 unidades de saldo
    arbol = {
        'tipo': 'accion',
        'texto': 'R',
        'hijos': [],
        'atributos': {
            'valido': True,
            'saldo': -3,
            'refrescos': 1,
            'nivel': 0,
            'errores': []
        }
    }
    p[0] = (True, [], -3, 1, 0, arbol)

def p_accion_devolver(p):
    'accion : DEVOLVER'
    # Devolver una moneda reduce el saldo en 1
    arbol = {
        'tipo': 'accion',
        'texto': '<',
        'hijos': [],
        'atributos': {
            'valido': True,
            'saldo': -1,
            'refrescos': 0,
            'nivel': 0,
            'errores': []
        }
    }
    p[0] = (True, [], -1, 0, 0, arbol)

def p_accion_bloque(p):
    'accion : LBRACE contenido RBRACE'
    # Extraer atributos del contenido interno
    contenido_valido, contenido_errores, contenido_saldo, contenido_refrescos, contenido_nivel, contenido_arbol = p[2]
    
    # Incrementar el nivel para el bloque anidado
    nivel_actual = contenido_nivel + 1
    
    # Verificar si no excede el máximo de niveles (3)
    nivel_valido = nivel_actual < 3
    
    # La validez depende del contenido y del nivel
    valido_final = contenido_valido and nivel_valido
    
    # Errores acumulados del contenido
    errores_final = contenido_errores.copy()
    
    # Agregar error si se excede el nivel
    if not nivel_valido:
        errores_final.append(f"Error: Nivel de anidamiento excesivo ({nivel_actual} > 3)")
    
    # Construir árbol de derivación
    arbol = {
        'tipo': 'accion_bloque',
        'texto': '{ C }',
        'hijos': [contenido_arbol],
        'atributos': {
            'valido': valido_final,
            'saldo': 0,  # Los bloques anidados no propagan saldo hacia afuera
            'refrescos': 0, # Los bloques anidados no propagan refrescos hacia afuera
            'nivel': nivel_actual,
            'errores': errores_final,
            'saldo_interno': contenido_saldo,
            'refrescos_interno': contenido_refrescos
        }
    }
    
    # Los bloques no propagan saldo ni refrescos
    p[0] = (valido_final, errores_final, 0, 0, nivel_actual, arbol)

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Error de sintaxis en '{p.value}'")
    else:
        print("Error de sintaxis en EOF")

# Crear el analizador sintáctico
parser = yacc.yacc()

def analizar(texto):
    # Análisis sintáctico y semántico integrado
    resultado = parser.parse(texto, lexer=lexer)
    return resultado

def validar_semanticamente(cadena):
    """Validación semántica mejorada que simula la ejecución de la máquina"""
    try:
        # Eliminar espacios
        cadena = cadena.strip()
        
        # Verificar estructura básica
        if not cadena.startswith('{') or not cadena.endswith('}'):
            return False, ["Error: La cadena debe estar entre llaves"], 0, 0, 0
        
        # Simular ejecución secuencial
        saldo = 0
        refrescos = 0
        nivel = 0
        errores = []
        pila_contextos = []  # Para manejar bloques anidados
        
        # Procesar cada carácter
        i = 1  # Empezar después de la llave inicial
        while i < len(cadena) - 1:  # Terminar antes de la llave final
            char = cadena[i]
            
            if char == '$':
                # Insertar moneda
                saldo += 1
                print(f"  Posición {i}: Moneda insertada: saldo = {saldo}")
                
            elif char == 'R':
                # Comprar refresco
                print(f"  Posición {i}: Intentando comprar refresco: saldo = {saldo}")
                if saldo >= 3:
                    saldo -= 3
                    refrescos += 1
                    print(f"  Refresco comprado: saldo = {saldo}, refrescos = {refrescos}")
                    if refrescos > 3:
                        errores.append(f"Error: Exceso de refrescos ({refrescos} > 3) en posición {i}")
                else:
                    errores.append(f"Error: Saldo insuficiente ({saldo} < 3) para comprar refresco en posición {i}")
                    
            elif char == '<':
                # Devolver moneda
                print(f"  Posición {i}: Intentando devolver moneda: saldo = {saldo}")
                if saldo >= 1:
                    saldo -= 1
                    print(f"  Moneda devuelta: saldo = {saldo}")
                else:
                    errores.append(f"Error: No hay monedas para devolver en posición {i}")
                    
            elif char == '{':
                # Inicio de bloque anidado
                print(f"  Posición {i}: Inicio de bloque: nivel {nivel} -> {nivel + 1}")
                pila_contextos.append({
                    'saldo_anterior': saldo,
                    'refrescos_anterior': refrescos,
                    'nivel_anterior': nivel
                })
                nivel += 1
                if nivel > 3:
                    errores.append(f"Error: Nivel de anidamiento excesivo ({nivel} > 3) en posición {i}")
                # El saldo se hereda en el bloque interno
                
            elif char == '}':
                # Final de bloque anidado
                if pila_contextos:
                    contexto_anterior = pila_contextos.pop()
                    print(f"  Posición {i}: Fin de bloque: nivel {nivel} -> {nivel - 1}")
                    print(f"    Saldo interno final: {saldo}, refrescos internos: {refrescos}")
                    
                    # Al salir del bloque, restaurar el contexto anterior
                    # pero mantener el saldo actualizado (el saldo sí se propaga)
                    refrescos = contexto_anterior['refrescos_anterior']  # Los refrescos no se propagan
                    nivel = contexto_anterior['nivel_anterior']
                    
                    print(f"    Restaurando contexto: saldo = {saldo}, refrescos = {refrescos}")
                else:
                    print(f"  Posición {i}: Cierre de bloque principal")
                    
            i += 1
        
        # Verificar que todos los bloques se cerraron correctamente
        if pila_contextos:
            errores.append("Error: Bloques sin cerrar")
        
        print(f"Resultado final: saldo = {saldo}, refrescos = {refrescos}, errores = {errores}")
        valido = len(errores) == 0
        return valido, errores, saldo, refrescos, max(0, nivel)
        
    except Exception as e:
        return False, [f"Error en validación semántica: {str(e)}"], 0, 0, 0

def validar_cadena(cadena):
    try:
        print(f"\n=== Analizando cadena: '{cadena}' ===")
        
        # Verificar que la cadena no esté vacía
        if not cadena:
            return False, "Cadena vacía", None
            
        # Primero hacer análisis sintáctico
        resultado_analisis = analizar(cadena)
        
        # Verificar si el análisis retornó None (error sintáctico)
        if resultado_analisis is None:
            return False, "Error de sintaxis", None
        
        # Extraer resultados del análisis sintáctico
        valido_sintactico, errores_sintacticos, saldo_sintactico, refrescos_sintacticos, nivel_sintactico, arbol = resultado_analisis
        
        print(f"Análisis sintáctico: válido={valido_sintactico}, errores={errores_sintacticos}")
        
        # Hacer validación semántica adicional
        valido_semantico, errores_semanticos, saldo_semantico, refrescos_semanticos, nivel_semantico = validar_semanticamente(cadena)
        
        print(f"Análisis semántico: válido={valido_semantico}, errores={errores_semanticos}")
        
        # Combinar resultados
        errores_finales = errores_sintacticos + errores_semanticos
        valido_final = valido_sintactico and valido_semantico and len(errores_finales) == 0
        
        # Usar los valores semánticos que son más precisos
        saldo_final = saldo_semantico
        refrescos_final = refrescos_semanticos
        nivel_final = max(nivel_sintactico, nivel_semantico)
        
        # Mensaje de resultado
        if valido_final:
            mensaje = "Cadena válida sintáctica y semánticamente"
        else:
            mensaje = f"Cadena inválida: {', '.join(errores_finales)}"
        
        # Resultado estructurado
        resultado = {
            'valido': valido_final,
            'mensaje': mensaje,
            'saldo_final': saldo_final,
            'refrescos': refrescos_final,
            'nivel': nivel_final,
            'errores': errores_finales,
            'arbol': arbol
        }
        
        print(f"Resultado final: valido={valido_final}, saldo={saldo_final}, refrescos={refrescos_final}")
        
        return valido_final, mensaje, resultado
    
    except Exception as e:
        print(f"Error al analizar '{cadena}': {str(e)}")
        return False, f"Error en el análisis: {str(e)}", None

def guardar_arbol_json(arbol, archivo):
    """Guarda el árbol de derivación en formato JSON para visualización externa"""
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(arbol, f, ensure_ascii=False, indent=2)

# Función principal para pruebas
def main():
    # Ejemplos de cadenas válidas
    cadenas_validas = [
        "{}",                # Bloque vacío
        "{$$$R}",            # Saldo suficiente para un refresco
        "{$$$$$$RR}",        # Saldo suficiente para dos refrescos
        "{$$$$$$RR{$$$R}}",  # Anidamiento válido con refrescos en ambos niveles
        "{$$$$$$RR{$$$R}<}", # Ejemplo problemático - debería ser válido
        "{$<}",              # Añadir una moneda y devolverla
        "{$$$$$$$$$RRR}",    # Máximo de refrescos permitidos
        "{$$$R{$$${R}}}",    # Anidamiento válido más complejo
        "{$$$$$$RR{$$$R}<}", # Prueba específica del error reportado
    ]
    
    # Ejemplos de cadenas inválidas semánticamente
    cadenas_invalidas = [
        "{R}",               # Refresco sin saldo suficiente
        "{$R}",              # Saldo insuficiente (se necesitan 3)
        "{$$$RR}",           # Segundo refresco sin saldo suficiente
        "{$$$R{$$$R{$$$R{$$$R}}}}",  # Exceso de anidamiento
        "{$$$RRRR}",         # Exceso de refrescos en un bloque
        "{<}",               # Devolución sin saldo
        "{$$<$R}",           # Saldo insuficiente después de devolver
        "{$$$R{$$$R}<}",     # Devolver cuando no hay saldo suficiente
    ]
    
    print("=== Pruebas con cadenas válidas ===")
    for i, cadena in enumerate(cadenas_validas):
        valido, mensaje, resultado = validar_cadena(cadena)
        print(f"Cadena {i+1}: '{cadena}'")
        print(f"Resultado: {mensaje}")
        if resultado:
            print(f"Saldo final: {resultado['saldo_final']}")
            print(f"Refrescos: {resultado['refrescos']}")
        print()
        
        # Guardar el árbol de la primera cadena válida para ejemplo
        if i == 0 and resultado:
            guardar_arbol_json(resultado['arbol'], "arbol_valido.json")
    
    print("=== Pruebas con cadenas inválidas ===")
    for i, cadena in enumerate(cadenas_invalidas):
        valido, mensaje, resultado = validar_cadena(cadena)
        print(f"Cadena {i+1}: '{cadena}'")
        print(f"Resultado: {mensaje}")
        print()
        
        # Guardar el árbol de la primera cadena inválida para ejemplo
        if i == 0 and resultado:
            guardar_arbol_json(resultado['arbol'], "arbol_invalido.json")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Si se proporciona un archivo como argumento
        if sys.argv[1] == "-i":
            # Modo interactivo
            print("Modo interactivo. Ingrese cadenas para analizar (Ctrl+C para salir):")
            try:
                while True:
                    entrada = input("> ")
                    valido, mensaje, resultado = validar_cadena(entrada)
                    print(f"Resultado: {mensaje}")
                    if valido:
                        print(f"Saldo final: {resultado['saldo_final']}")
                        print(f"Refrescos: {resultado['refrescos']}")
                    else:
                        print(f"Errores: {', '.join(resultado['errores'])}")
            except KeyboardInterrupt:
                print("\nSaliendo del modo interactivo.")
        else:
            # Procesar archivo
            with open(sys.argv[1], 'r', encoding='utf-8') as file:
                codigo = file.read()
            valido, mensaje, resultado = validar_cadena(codigo)
            print(f"Resultado: {mensaje}")
            if valido:
                print(f"Saldo final: {resultado['saldo_final']}")
                print(f"Refrescos: {resultado['refrescos']}")
            else:
                print(f"Errores: {', '.join(resultado['errores'] if resultado else ['Error de análisis'])}")
            
            # Guardar el árbol para visualización
            if resultado and 'arbol' in resultado:
                guardar_arbol_json(resultado['arbol'], "arbol_analisis.json")
                print("Árbol de derivación guardado en 'arbol_analisis.json'")
    else:
        # Ejecutar pruebas predefinidas
        main()
