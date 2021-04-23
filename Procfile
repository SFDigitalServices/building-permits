web: pipenv run gunicorn 'service.microservice:start_service()'
worker: pipenv run celery worker -Ofair
celery_beat: pipenv run celery -A tasks beat --loglevel=info