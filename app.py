import os
from flask import Flask, render_template, request, jsonify
from maquina_expendedora import validar_cadena

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar_cadena():
    datos = request.get_json()
    cadena = datos.get('cadena', '')
    
    if not cadena:
        return jsonify({
            'valido': False,
            'mensaje': 'Por favor ingrese una cadena para analizar',
            'arbol': None,
            'estadisticas': {
                'saldo_final': 0,
                'num_refrescos': 0,
                'valido_semantico': False,
                'errores': ['Cadena vacía'],
                'niveles': {}
            }
        })
    
    valido, mensaje, resultado = validar_cadena(cadena)
    
    # Procesar el árbol para visualización
    arbol_visual = procesar_arbol_decorado(resultado['arbol']) if resultado and 'arbol' in resultado else None
    
    # Imprimir para debug
    print(f"Cadena analizada: {cadena}")
    print(f"Resultado valido: {valido}")
    print(f"Estructura del árbol: {arbol_visual is not None}")
    
    # Calcular estadísticas
    estadisticas = {
        'saldo_final': resultado['saldo_final'] if resultado else 0,
        'num_refrescos': resultado['refrescos'] if resultado else 0,
        'valido_semantico': valido,
        'errores': resultado['errores'] if resultado else ['Error en el análisis'],
        'niveles': extraer_niveles_anidados(resultado['arbol']) if resultado and 'arbol' in resultado else {}
    }
    
    return jsonify({
        'valido': valido,
        'mensaje': mensaje,
        'arbol': arbol_visual,
        'estadisticas': estadisticas
    })

def procesar_arbol_decorado(nodo, nivel=0):
    """Convierte el árbol semántico a un formato adecuado para visualización en D3.js"""
    if not nodo:
        return None
        
    # Verificar si el nodo es una tupla (formato antiguo)
    if isinstance(nodo, tuple):
        print(f"Detectado nodo en formato de tupla: {nodo}")
        # Convertir de formato antiguo (tupla) a diccionario para compatibilidad
        if len(nodo) >= 6:
            tipo_nodo = "programa" if nivel == 0 else "bloque"
            valido, errores, saldo, refrescos, nivel_nodo, hijos = nodo
            nodo = {
                'tipo': tipo_nodo,
                'valido': valido,
                'errores': errores,
                'saldo_final': saldo,
                'refrescos': refrescos,
                'nivel': nivel_nodo,
                'hijos': [hijos] if hijos else []
            }
    
    # Inicializar la información del nodo para visualización
    node_info = {
        'tipo': nodo.get('tipo', 'desconocido'),
        'hijos': [],
        'valido': len(nodo.get('errores', [])) == 0,
        'nivel': nodo.get('nivel', nivel),
        'saldo': nodo.get('saldo_final', 0),
        'refrescos': nodo.get('refrescos', 0),
        'errores': nodo.get('errores', [])
    }
    
    # Procesar los diferentes tipos de nodos
    try:
        if node_info['tipo'] == 'maquina':
            # Procesar el bloque principal
            if 'bloque' in nodo:
                bloque_visual = procesar_arbol_decorado(nodo['bloque'], nivel)
                if bloque_visual:
                    node_info['hijos'].append(bloque_visual)
        
        elif node_info['tipo'] == 'programa':
            # Caso especial para el nodo programa en formato antiguo
            for hijo in nodo.get('hijos', []):
                hijo_visual = procesar_arbol_decorado(hijo, nivel+1)
                if hijo_visual:
                    node_info['hijos'].append(hijo_visual)
        
        elif node_info['tipo'] == 'bloque':
            # Procesar el contenido del bloque
            if 'contenido' in nodo:
                contenido_visual = procesar_arbol_decorado(nodo['contenido'], nivel + 1)
                if contenido_visual:
                    node_info['hijos'].append(contenido_visual)
            # Para formato antiguo
            elif 'hijos' in nodo:
                for hijo in nodo.get('hijos', []):
                    hijo_visual = procesar_arbol_decorado(hijo, nivel+1)
                    if hijo_visual:
                        node_info['hijos'].append(hijo_visual)
        
        elif node_info['tipo'] == 'operaciones':
            # Procesar cada operación individual
            for op in nodo.get('operaciones', []):
                op_visual = procesar_arbol_decorado(op, nivel)
                if op_visual:
                    node_info['hijos'].append(op_visual)
        
        elif node_info['tipo'] == 'operacion_moneda':
            # Nodo hoja para operación de moneda
            node_info['texto'] = '$'
        
        elif node_info['tipo'] == 'operacion_refresco':
            # Nodo hoja para operación de comprar refresco
            node_info['texto'] = 'R'
        
        elif node_info['tipo'] == 'operacion_cambio':
            # Nodo hoja para operación de devolver cambio
            node_info['texto'] = '<'
        
        elif node_info['tipo'] == 'operacion_subbloque':
            # Procesar el subbloque anidado
            if 'bloque' in nodo:
                subbloque_visual = procesar_arbol_decorado(nodo['bloque'], nivel + 1)
                if subbloque_visual:
                    node_info['hijos'].append(subbloque_visual)
        
        # Tipos adicionales de nodo del formato antiguo
        elif node_info['tipo'] == 'contenido' or node_info['tipo'] == 'accion':
            texto = nodo.get('texto', node_info['tipo'])
            node_info['texto'] = texto
            # Si hay hijos, procesarlos recursivamente
            if 'hijos' in nodo and nodo['hijos']:
                for hijo in nodo['hijos']:
                    hijo_visual = procesar_arbol_decorado(hijo, nivel+1)
                    if hijo_visual:
                        node_info['hijos'].append(hijo_visual)
    except Exception as e:
        print(f"Error al procesar nodo {node_info['tipo']}: {str(e)}")
        
    # Agregar información de atributos para visualización
    node_info['atributos'] = {
        'saldo_inicial': nodo.get('saldo_inicial', 0),
        'saldo_final': nodo.get('saldo_final', 0),
        'refrescos': nodo.get('refrescos', 0),
        'nivel': nodo.get('nivel', nivel),
        'errores': nodo.get('errores', [])
    }
    
    # Texto a mostrar en la visualización
    if 'texto' not in node_info:
        node_info['texto'] = f"{node_info['tipo']} (S:{node_info['saldo']})"
    
    return node_info
    
    # Agregar información de atributos para visualización
    node_info['atributos'] = {
        'saldo_inicial': nodo.get('saldo_inicial', 0),
        'saldo_final': nodo.get('saldo_final', 0),
        'refrescos': nodo.get('refrescos', 0),
        'nivel': nodo.get('nivel', nivel),
        'errores': nodo.get('errores', [])
    }
    
    # Texto a mostrar en la visualización
    if 'texto' not in node_info:
        node_info['texto'] = f"{nodo['tipo']} (S:{node_info['saldo']})"
    
    return node_info

def extraer_niveles_anidados(arbol, nivel=0, resultado=None):
    """Extrae la información de niveles anidados para estadísticas"""
    if resultado is None:
        resultado = {}
    
    if not arbol:
        return resultado
    
    # Inicializar nivel si no existe
    nivel_actual = arbol.get('nivel', nivel)
    if str(nivel_actual) not in resultado:
        resultado[str(nivel_actual)] = {
            'saldo': 0,
            'refrescos': 0,
            'bloques': 0
        }
    
    # Actualizar estadísticas del nivel actual
    if arbol.get('tipo') == 'bloque':
        resultado[str(nivel_actual)]['bloques'] += 1
    
    resultado[str(nivel_actual)]['saldo'] += arbol.get('saldo_final', 0) - arbol.get('saldo_inicial', 0)
    resultado[str(nivel_actual)]['refrescos'] += arbol.get('refrescos', 0)
    
    # Procesar nodos hijos recursivamente
    if arbol.get('tipo') == 'maquina' and 'bloque' in arbol:
        extraer_niveles_anidados(arbol['bloque'], nivel_actual, resultado)
    
    elif arbol.get('tipo') == 'bloque' and 'contenido' in arbol:
        extraer_niveles_anidados(arbol['contenido'], nivel_actual, resultado)
    
    elif arbol.get('tipo') == 'operaciones' and 'operaciones' in arbol:
        for op in arbol['operaciones']:
            extraer_niveles_anidados(op, nivel_actual, resultado)
    
    elif arbol.get('tipo') == 'operacion_subbloque' and 'bloque' in arbol:
        extraer_niveles_anidados(arbol['bloque'], nivel_actual + 1, resultado)
    
    return resultado

if __name__ == '__main__':
    app.run(debug=True)
