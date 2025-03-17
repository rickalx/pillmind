from telegram.ext import Application
from dotenv import load_dotenv

from chatbot_handler import setup_handlers, TOKEN

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def main():
    # Crear la aplicación con el token
    application = Application.builder().token(TOKEN).build()
    
    # Configurar los manejadores desde chatbot_handler
    application = setup_handlers(application)
    
    # Iniciar el bot
    application.run_polling()
    
    return application

if __name__ == '__main__':
    main()
