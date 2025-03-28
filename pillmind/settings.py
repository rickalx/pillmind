"""
Django settings for pillmind project.

Generated by 'django-admin startproject' using Django 5.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os
import dj_database_url

load_dotenv()
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == 'development':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'pillmind.up.railway.app']

CSRF_TRUSTED_ORIGINS = ['https://pillmind.up.railway.app']

SECURE_SSL_REDIRECT = False

SECURE_HSTS_SECONDS = 31536000  # 1 año en segundos
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Aplica HSTS a subdominios
SECURE_HSTS_PRELOAD = True  # Permite que tu dominio sea incluido en la lista de precarga de HSTS

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'webapp',
    #'corsheaders',#eliminar para producción
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Agregar después de SecurityMiddleware
    #'corsheaders.middleware.CorsMiddleware',  # elimina para prod
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pillmind.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pillmind.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    ),
}

POSTGRES_LOCALLY = True
if ENVIRONMENT == 'production' or POSTGRES_LOCALLY == True:
    DATABASES['default']=dj_database_url.parse(os.getenv('DATABASE_PUBLIC_URL'))


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Guayaquil'  # Para Ecuador

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

# Directorio donde se recopilarán los archivos estáticos
STATIC_ROOT = BASE_DIR / "staticfiles"

# Directorios adicionales donde buscar archivos estáticos
STATICFILES_DIRS = [BASE_DIR / "webapp/static"]

# Opcional: compresión y cacheo de archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'webapp.CustomUser'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'localtime': {
            '()': 'utils.logging_config.LocalTimeFormatter',
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'errores.log',
            'formatter': 'localtime',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'pillmind': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Ejemplo: frontend en React
    "http://127.0.0.1:8000",  # Permitir el dominio local
]

LOGIN_REDIRECT_URL = '/'  # Redirige al inicio después de iniciar sesión
LOGOUT_REDIRECT_URL = '/'  # Redirige al inicio después de cerrar sesión
LOGIN_URL = '/accounts/login/'  # Ruta para la vista de inicio de sesión

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False