"""
Contiene el prompt predeterminado para usar como fallback cuando
no se puede obtener uno de la base de datos.
"""

# Leer el contenido del archivo de texto
import os

def _load_prompt():
    """Carga el prompt predeterminado desde el archivo de texto"""
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt_predeterminado.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Eliminar la primera línea que contiene el nombre del prompt
            lines = content.split('\n')
            if lines and lines[0].startswith('#'):
                content = '\n'.join(lines[1:])
            return content.strip()
    except Exception as e:
        print(f"Error al cargar el prompt predeterminado: {e}")
        return "Actúa como: Analista Político Senior\n\nAnaliza la siguiente propuesta política en Ecuador, devolviendo una respuesta de maximo 10 lineas:"

# Cargar el prompt al importar el módulo
DEFAULT_PROMPT = _load_prompt()