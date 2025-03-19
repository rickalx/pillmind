import os
import uuid
from google import genai
from google.genai import types
from utils.logging_config import logger  # Import the logger
from webapp.models.prompt import Prompt
from asgiref.sync import sync_to_async

# Importar el prompt predeterminado al inicio del programa
from .prompt_predeterminado import DEFAULT_PROMPT

# Crear una excepción personalizada para este tipo de error específico
class PromptDatabaseError(Exception):
    """Excepción para errores relacionados con la obtención de prompts de la base de datos"""
    pass

# Función interna que realiza las operaciones sincrónicas
def _get_prompt_from_database_sync():
    """Versión sincrónica de la función para obtener el prompt"""
    try:
        default_prompt = Prompt.objects.filter(es_predeterminado=True).first()
        if default_prompt:
            prompt_text = default_prompt.texto
            rol_nombre = default_prompt.rol_ia.nombre if default_prompt.rol_ia else "Analista Político Senior"
            
            # Combinar el rol con el texto del prompt
            full_prompt = f"Actúa como: {rol_nombre}\n\n{prompt_text}"
            
            # Añadir formato de respuesta si existe
            if hasattr(default_prompt, 'formato_respuesta') and default_prompt.formato_respuesta:
                full_prompt += f"\n\n[FORMATO DE RESPUESTA]\n{default_prompt.formato_respuesta}"
                        
            return full_prompt
        else:
            # En lugar de devolver un valor predeterminado, lanzamos excepción
            raise PromptDatabaseError("No se encontró un prompt predeterminado en la base de datos")
    except Exception as e:
        # Loguear y relanzar como una excepción personalizada
        logger.error(f"Error al obtener prompt de la base de datos: {str(e)}")
        raise PromptDatabaseError(f"Error al obtener prompt de la base de datos: {str(e)}")

# Versión asincrónica que llama a la versión sincrónica
get_prompt_from_database = sync_to_async(_get_prompt_from_database_sync, thread_sensitive=False)

def get_default_prompt_id():
    """Obtiene el ID del prompt predeterminado"""
    default_prompt = Prompt.objects.filter(es_predeterminado=True).first()
    if default_prompt:
        return default_prompt.id
    return None

# Modificar la función generate para hacerla correctamente asincrónica
async def generate(texto):
    logger.info("Iniciando generación de análisis con IA")
    
    # Truncar logging del texto si es muy largo
    log_texto = texto[:100] + "..." if len(texto) > 100 else texto
    logger.debug(f"Texto a analizar (truncado): {log_texto}")
    
    try:
        # Primera modificación importante: usar try/except específico para el prompt
        try:
            # Segunda modificación importante: usar await con la función asíncrona
            prompt = await get_prompt_from_database()
            logger.debug("Prompt obtenido correctamente desde la base de datos")
        except Exception as e:
            # Si hay error al obtener el prompt, usar el prompt externo cargado al inicio
            logger.error(f"Error al obtener prompt de la base de datos: {str(e)}")
            prompt = DEFAULT_PROMPT
            logger.debug("Usando prompt predeterminado del archivo externo")
        
        client = genai.Client(
            api_key=os.environ.get("IA_API_KEY"),
        )
        logger.debug("Cliente de Gemini inicializado")

        model = "gemini-2.0-flash-thinking-exp-01-21"
        logger.info(f"Usando modelo: {model}")
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=f"{prompt}\n\nPropuesta: {texto}"),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=0.3,
            top_p=0.8,
            top_k=30,
            max_output_tokens=65536,
            response_mime_type="text/plain",
        )
        logger.debug(f"Configuración generada: temperatura={generate_content_config.temperature}, max_tokens={generate_content_config.max_output_tokens}")

        full_response = ""  # Variable para acumular la respuesta completa
        logger.debug("Iniciando streaming de respuesta")

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            full_response += chunk.text  # Acumular cada fragmento de texto en la variable
        
        # Log tamaño de respuesta y primeras palabras
        resp_preview = full_response[:100] + "..." if len(full_response) > 100 else full_response
        logger.info(f"Respuesta generada: {len(full_response)} caracteres. Vista previa: {resp_preview}")
        
        return full_response  # Retornar la respuesta completa
    
    except Exception as e:
        logger.error(f"Error al generar análisis con IA: {str(e)}", exc_info=True)
        return f"Error en la generación del análisis: {str(e)}"

def guardar_analisis_propuesta(usuario, url_propuesta, contenido, prompts_utilizados=None):
    """Guarda el análisis de propuesta en la base de datos"""
    # Inicializar como lista vacía si es None
    if prompts_utilizados is None:
        prompts_utilizados = []
    
    # Si la lista está vacía, intentar obtener el prompt predeterminado
    if len(prompts_utilizados) == 0:
        default_prompt_id = get_default_prompt_id()
        # Solo usar prompt_id si realmente existe, convertido a string para JSON
        prompts_utilizados = [str(default_prompt_id)] if default_prompt_id else []
        
        # Si aún no hay prompts, guardar sin relacionarlos
        if not prompts_utilizados:
            logger.warning("No se encontró un prompt predeterminado, el análisis se guardará sin relacionarse a ningún prompt")
    else:
        # Convertir cualquier UUID en la lista a string para que sea serializable a JSON
        prompts_utilizados = [str(p_id) if isinstance(p_id, uuid.UUID) else p_id for p_id in prompts_utilizados]

if __name__ == "__main__":
    texto = "Tu texto aquí"
    response = generate(texto)
    print(response)
