# Máquina Expendedora con Bloques Anidados

## Camacho Zavala Ricardo
## Valverde Rojas Gustavo

## Reglas Semánticas

1. Cada bloque `{ ... }` posee su propio saldo local, independiente del bloque exterior.
2. Un refresco (R) solo puede comprarse si el saldo local es mayor o igual a 3.
3. Al usar `<`, las monedas no utilizadas se pierden, no se heredan fuera del bloque.
4. Se permite un máximo de 3 niveles de anidamiento.
5. Cada bloque puede contener como máximo 3 refrescos (R).

## Símbolos de la Gramática

- `$` - Insertar una moneda (aumenta el saldo en 1)
- `R` - Comprar un refresco (cuesta 3 monedas)
- `<` - Devolver una moneda (reduce el saldo en 1)
- `{ }` - Define un bloque con saldo independiente


## Requisitos

- Python 3.6 o superior
- Flask
- PLY (Python Lex-Yacc)

## Instalación

1. Crear un entorno virtual:

```bash
python -m venv venv
```
2. Antes de activar el entorno (solo mientras está abierta la terminal actual) ejecutar:

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

3. Activar el entorno virtual:

   ```bash
   .\venv\Scripts\activate
   ```
  
4. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

5. Ejecutar el servidor:

```bash
python app.py
```

**Nota**: Si encuentras errores relacionados con `werkzeug.urls` o `url_quote`, asegúrate de tener las versiones compatibles en requirements.txt (Flask==2.0.1 y werkzeug==2.0.3).

6. Abrir en el navegador:
   - http://localhost:5000

## Cómo usar

1. Ingrese una cadena en el área de texto siguiendo la gramática definida
   - Ejemplo: `{$$$R}`
2. La aplicación analizará automáticamente la cadena mientras escribe
3. El resultado del análisis se mostrará en la sección derecha
4. Se visualizará el estado de la máquina y los errores, si los hay
5. Se mostrarán estadísticas sobre la ejecución

## Ejemplos de cadenas válidas

- `{}` - Bloque vacío
- `{$$$R}` - Insertar 3 monedas y comprar un refresco
- `{$$$R{$$$R}}` - Bloque anidado con un refresco en cada nivel
- `{$<}` - Insertar una moneda y devolverla

## Ejemplos de cadenas inválidas

- `{R}` - Intentar comprar un refresco sin saldo suficiente
- `{$R}` - Saldo insuficiente (se necesitan 3 monedas)
- `{$$$RRRR}` - Exceso de refrescos en un bloque (máximo 3)
- `{$$$R{$$$R{$$$R{$$$R}}}}` - Exceso de anidamiento (máximo 3 niveles)
