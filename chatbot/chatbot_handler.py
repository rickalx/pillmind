from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, MessageHandler, filters
import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import logging

from ai_handler import generate

# Configurar el logging
#logging.basicConfig(filename='errores.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='errores.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener el token y la URL de la API desde las variables de entorno
TOKEN = os.getenv('TOKEN')

async def start(update, context):
    context.user_data['pregunta_actual'] = 1
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hola, soy FactibleBot, un asistente de inteligencia artificial que te ayudará a evaluar la factibilidad de propuestas de campaña política.")
    await pregunta(update, context)

async def pregunta(update, context):
    pregunta_actual = context.user_data['pregunta_actual']

    if pregunta_actual == 1:
        texto_pregunta = "¿Qué tan realista crees que es la propuesta?"
        opciones = [["Muy realista", "muy_realista"], ["Parcialmente realista", "parcialmente_realista"], ["Poco realista", "poco_realista"], ["No realista", "no_realista"]]
    elif pregunta_actual == 2:
        texto_pregunta = "¿Qué tan relevante es esta propuesta para tus necesidades e intereses?"
        opciones = [["Muy relevante", "muy_relevante"], ["Parcialmente relevante", "parcialmente_relevante"], ["Poco relevante", "poco_relevante"], ["No relevante", "no_relevante"]]
    elif pregunta_actual == 3:
        texto_pregunta = "¿Qué tan confiable te parece el candidato que propone esta idea?"
        opciones = [["Muy confiable", "muy_confiable"], ["Parcialmente confiable", "parcialmente_confiable"], ["Poco confiable", "poco_confiable"], ["No confiable", "no_confiable"]]
    elif pregunta_actual == 4:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Envíame el link de una propuesta y te devolveré un análisis de si es viable o no.")
        return
    elif pregunta_actual == 5:
        texto_pregunta = "¿Quieres evaluar otra propuesta?"
        opciones = [["Evaluar otra propuesta", "otra_propuesta"], ["Salir", "salir"]]
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Gracias por tus respuestas!")
        return

    keyboard = [[InlineKeyboardButton(opcion[0], callback_data=opcion[1]) for opcion in opciones]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if pregunta_actual > 1:
        # Obtener el mensaje actual
        current_message = context.user_data.get('mensaje_pregunta')
        if current_message:
            # Verificar si el contenido o el markup han cambiado
            if current_message.text != texto_pregunta or current_message.reply_markup != reply_markup:
                await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=current_message.message_id, text=texto_pregunta, reply_markup=reply_markup)
            else:
                logging.info("El mensaje no se modificó porque el contenido y el markup son los mismos.")
        else:
            mensaje = await context.bot.send_message(chat_id=update.effective_chat.id, text=texto_pregunta, reply_markup=reply_markup)
            context.user_data['mensaje_pregunta'] = mensaje
    else:
        mensaje = await context.bot.send_message(chat_id=update.effective_chat.id, text=texto_pregunta, reply_markup=reply_markup)
        context.user_data['mensaje_pregunta'] = mensaje

async def respuesta(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "otra_propuesta":
        context.user_data['pregunta_actual'] = 1
        await pregunta(update, context)
    elif query.data == "salir":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Hasta luego!")
    else:
        context.user_data['pregunta_actual'] += 1
        await pregunta(update, context)

async def send_long_message(bot, chat_id, text):
    """Envía un mensaje largo en partes más pequeñas."""
    max_length = 4096
    for i in range(0, len(text), max_length):
        await bot.send_message(chat_id=chat_id, text=text[i:i+max_length], parse_mode='HTML')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los mensajes de texto que no son URLs."""
    # Verificar si es la primera interacción del usuario
    if 'ha_iniciado' not in context.user_data:
        context.user_data['ha_iniciado'] = True
        # Enviar mensaje de bienvenida
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hola, soy FactibleBot, un asistente de inteligencia artificial que te ayudará a evaluar la factibilidad de propuestas de campaña política.")
        context.user_data['pregunta_actual'] = 1
        await pregunta(update, context)
    else:
        # Enviar directamente la pregunta 5 como un nuevo mensaje
        texto_pregunta = "¿Quieres evaluar otra propuesta o salir?"
        opciones = [["Evaluar otra propuesta", "otra_propuesta"], ["Salir", "salir"]]
        keyboard = [[InlineKeyboardButton(opcion[0], callback_data=opcion[1]) for opcion in opciones]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        mensaje = await context.bot.send_message(chat_id=update.effective_chat.id, text=texto_pregunta, reply_markup=reply_markup)
        context.user_data['mensaje_pregunta'] = mensaje
        context.user_data['pregunta_actual'] = 5
        logging.info("Pregunta 5 enviada directamente desde handle_text")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los mensajes que contienen URLs."""
    # Verificar si es la primera interacción del usuario
    if 'ha_iniciado' not in context.user_data:
        context.user_data['ha_iniciado'] = True
        # Enviar mensaje de bienvenida
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hola, soy FactibleBot, un asistente de inteligencia artificial que te ayudará a evaluar la factibilidad de propuestas de campaña política.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Evaluando, por favor espera un momento...")

    url = update.message.text

    try:
        logging.info(f"Procesando URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        texto = soup.get_text().strip()
        logging.info(f"Texto extraído: {texto[:100]}...")  # Log solo los primeros 100 caracteres

        respuesta_ia = generate(texto)
        logging.info(f"Respuesta generada: {respuesta_ia[:100]}...")  # Log solo los primeros 100 caracteres

        await send_long_message(context.bot, update.effective_chat.id, respuesta_ia)
        # await agregar_datos_desde_texto(respuesta_ia)
        
        # Enviar mensaje adicional sobre la página web
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Si quieres profundizar, puedes visitar nuestra pagina web: https://www.dataec593.com/pillmind/")
        
        # Enviar directamente la pregunta 5 como un nuevo mensaje
        texto_pregunta = "¿Quieres evaluar otra propuesta o salir?"
        opciones = [["Evaluar otra propuesta", "otra_propuesta"], ["Salir", "salir"]]
        keyboard = [[InlineKeyboardButton(opcion[0], callback_data=opcion[1]) for opcion in opciones]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        mensaje = await context.bot.send_message(chat_id=update.effective_chat.id, text=texto_pregunta, reply_markup=reply_markup)
        context.user_data['mensaje_pregunta'] = mensaje
        context.user_data['pregunta_actual'] = 5
        logging.info("Pregunta 5 enviada directamente desde handle_url")

    except requests.exceptions.RequestException as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al procesar la URL: {e}")
        logging.error(f"Error al procesar la URL: {e}")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error inesperado: {e}")
        logging.error(f"Error inesperado: {e}")

def setup_handlers(application):
    """Configura los manejadores para la aplicación del bot."""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Entity('url'), handle_url))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.Entity('url'), handle_text))
    application.add_handler(CallbackQueryHandler(respuesta))
    
    return application
