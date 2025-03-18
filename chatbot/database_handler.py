import logging
import uuid
from django.utils import timezone
from webapp.models.analisis_propuesta import AnalisisPropuesta
from webapp.models.prompt import Prompt
from asgiref.sync import sync_to_async
from utils.logging_config import logger  # Importar el logger centralizado

def guardar_analisis_propuesta(usuario, url_propuesta, contenido, prompts_utilizados=None):
    """
    Guarda un análisis de propuesta en la base de datos.
    
    Args:
        usuario: El usuario que hizo la solicitud.
        url_propuesta: La URL de la propuesta.
        contenido: El contenido del análisis generado por la IA.
        prompts_utilizados: Los prompts utilizados en el análisis (formato JSON).
    """
    logger.info(f"Iniciando guardado de análisis - URL: {url_propuesta} - Usuario: {getattr(usuario, 'username', 'desconocido')}")
    
    # CAMBIO AQUÍ: Inicializar como lista vacía, no como None
    if prompts_utilizados is None:
        prompts_utilizados = []
    
    # Si la lista está vacía, intentar obtener el prompt predeterminado
    if len(prompts_utilizados) == 0:
        default_prompt_id = get_default_prompt_id()
        if default_prompt_id:
            # Solo agregar el ID si realmente existe, pero convertido a string para JSON
            prompts_utilizados = [str(default_prompt_id)]
            logger.debug(f"Usando prompt predeterminado con ID: {default_prompt_id}")
        else:
            # Mantener la lista vacía si no hay prompt predeterminado
            prompts_utilizados = []
            logger.warning("No se encontró un prompt predeterminado, el análisis se guardará sin relacionarse a ningún prompt")
    else:
        # Convertir cualquier UUID en la lista a string para que sea serializable a JSON
        prompts_utilizados = [str(p_id) if isinstance(p_id, uuid.UUID) else p_id for p_id in prompts_utilizados]
    
    try:
        # Determinar nombre y email del usuario
        # Si el usuario es del chatbot (sin email), usar valores genéricos
        nombre_usuario = "usuario_chatbot"
        email_usuario = "usuario_chatbot@email.com"
        
        # Extraer información del usuario si está disponible
        if usuario:
            try:
                if hasattr(usuario, 'username') and usuario.username:
                    nombre_usuario = usuario.username
                    logger.debug(f"Username encontrado: {nombre_usuario}")
                elif hasattr(usuario, 'first_name'):  # Para usuarios de Telegram
                    nombre_usuario = usuario.first_name
                    logger.debug(f"First name usado como username: {nombre_usuario}")
                    
                if hasattr(usuario, 'email') and usuario.email:
                    email_usuario = usuario.email
                    logger.debug(f"Email encontrado: {email_usuario}")
            except AttributeError:
                logger.warning(f"Usuario del chatbot detectado, usando valores genéricos - Tipo: {type(usuario)}")
        
        logger.info(f"Creando registro con nombre: {nombre_usuario}, email: {email_usuario}")
        # Crear una nueva instancia de AnalisisPropuesta con usuario=None (no usar el objeto Telegram User)
        analisis = AnalisisPropuesta(
            usuario=None,  # No asignar el usuario de Telegram directamente
            nombre_usuario=nombre_usuario,
            email_usuario=email_usuario,
            url_propuesta=url_propuesta,
            contenido=contenido,
            prompts_utilizados=prompts_utilizados,
            estado=AnalisisPropuesta.Estado.BORRADOR,
            fecha_analisis=timezone.now()
        )
        
        # Guardar la instancia en la base de datos
        analisis.save()
        logger.info(f"Análisis guardado con ID: {analisis.id}")
        
        # CORRECCIÓN: Manejo mejorado de prompts_utilizados
        # Si hay prompts_utilizados, intentar relacionarlos
        if prompts_utilizados:
            # Validar que los IDs sean UUIDs válidos o transformarlos si es posible
            valid_prompt_ids = []
            for prompt_id in prompts_utilizados:
                try:
                    # Intentar convertir a UUID si es un string
                    if isinstance(prompt_id, str):
                        uuid_obj = uuid.UUID(prompt_id)
                        valid_prompt_ids.append(uuid_obj)
                    elif isinstance(prompt_id, uuid.UUID):
                        valid_prompt_ids.append(prompt_id)
                    else:
                        logger.warning(f"ID de prompt con formato inválido: {prompt_id}")
                except ValueError:
                    logger.warning(f"No se puede convertir a UUID: {prompt_id}")
            
            # Usar los IDs validados
            for prompt_id in valid_prompt_ids:
                try:
                    prompt = Prompt.objects.get(id=prompt_id)
                    analisis.prompts.add(prompt)
                    logger.debug(f"Prompt relacionado con ID: {prompt_id}")
                except Prompt.DoesNotExist:
                    logger.warning(f"El prompt con ID {prompt_id} no existe en la base de datos")
        # Si no hay prompts_utilizados o la lista está vacía, intentar usar el predeterminado
        elif not prompts_utilizados or len(prompts_utilizados) == 0:
            try:
                default_prompt = Prompt.objects.filter(es_predeterminado=True).first()
                if default_prompt:
                    analisis.prompts.add(default_prompt)
                    logger.debug(f"Prompt predeterminado relacionado con ID: {default_prompt.id}")
            except Exception as e:
                logger.warning(f"No se pudo relacionar el prompt predeterminado: {e}")
        else:
            logger.info("No se especificaron prompts para relacionar con el análisis")
                
        logger.info(f"Análisis de propuesta guardado exitosamente: {analisis}")
        return analisis
    
    except Exception as e:
        logger.error(f"Error al guardar el análisis de propuesta: {e}", exc_info=True)
        raise

# Versión asíncrona de la función para usar desde el chatbot
async def guardar_analisis_propuesta_async(usuario, url_propuesta, contenido, prompts_utilizados):
    """
    Versión asíncrona para guardar un análisis de propuesta en la base de datos.
    Para uso desde contextos asíncronos como el chatbot.
    
    Args:
        usuario: El usuario que hizo la solicitud.
        url_propuesta: La URL de la propuesta.
        contenido: El contenido del análisis generado por la IA.
        prompts_utilizados: Los prompts utilizados en el análisis (formato JSON).
    """
    logger.info(f"Iniciando guardado asíncrono de análisis - URL: {url_propuesta}")
    # Utilizamos sync_to_async para convertir la función síncrona a asíncrona
    guardar_func = sync_to_async(guardar_analisis_propuesta)
    try:
        resultado = await guardar_func(usuario, url_propuesta, contenido, prompts_utilizados)
        logger.info("Guardado asíncrono completado exitosamente")
        return resultado
    except Exception as e:
        logger.error(f"Error en guardado asíncrono: {e}", exc_info=True)
        raise

def get_default_prompt_id():
    """Obtiene el ID del prompt predeterminado"""
    try:
        default_prompt = Prompt.objects.filter(es_predeterminado=True).first()
        if default_prompt:
            return default_prompt.id  # Debe ser un UUID
        return None
    except Exception as e:
        logger.error(f"Error al obtener prompt predeterminado: {e}")
        return None
