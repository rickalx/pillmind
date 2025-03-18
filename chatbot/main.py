import os
import sys
import django
from telegram.ext import Application
from dotenv import load_dotenv

# Configurar el entorno de Django antes de importar módulos que usen Django
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pillmind.settings')
django.setup()

# Ahora se puede importar módulos que usen Django
from .chatbot_handler import setup_handlers, TOKEN  # Importación absoluta

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

#how to run the code:
#uv run -m chatbot.main
#todo: search how to run the chatbot when we run the webapp