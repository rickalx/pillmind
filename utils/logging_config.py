import os
import logging
import pytz  # Necesitarás instalar esta biblioteca
from datetime import datetime
from pathlib import Path
from django.conf import settings

class LocalTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # Convertir a la zona horaria configurada en Django
        dt = datetime.fromtimestamp(record.created)
        if settings.USE_TZ:
            dt = dt.replace(tzinfo=pytz.UTC)
            dt = dt.astimezone(pytz.timezone(settings.TIME_ZONE))
        return dt.strftime(datefmt) if datefmt else dt.isoformat()

def setup_logging():
    """
    Configuración centralizada del logging para toda la aplicación.
    Crea un directorio de logs y configura el logger principal.
    
    Returns:
        Logger: El logger configurado
    """
    # Configurar el logging con rutas absolutas
    BASE_DIR = Path(__file__).resolve().parent.parent  # pillmind directory
    LOG_FILE = BASE_DIR / 'logs' / 'errores.log'

    # Crear el directorio logs si no existe
    os.makedirs(LOG_FILE.parent, exist_ok=True)
    
    # Crear logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Crear handler para el archivo
    file_handler = logging.FileHandler(str(LOG_FILE))
    file_handler.setLevel(logging.INFO)
    
    # Usar el formateador personalizado para la zona horaria
    formatter = LocalTimeFormatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Añadir el handler al logger
    logger.addHandler(file_handler)
    
    return logger

# Crear una instancia del logger disponible para importar
logger = setup_logging()
