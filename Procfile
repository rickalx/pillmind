web: python manage.py collectstatic --noinput && python manage.py loaddata datos.json && gunicorn pillmind.wsgi
worker: python -m chatbot.main