web: gunicorn Balie_Sauny.wsgi --log-file -
release: python manage.py migrate && python manage.py collectstatic --noinput