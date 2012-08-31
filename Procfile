web: gunicorn testdjango.wsgi -b 0.0.0.0:$PORT
celeryd: python manage.py celeryd -E -B --loglevel=INFO
celerybeat: python manage.py celerybeat
