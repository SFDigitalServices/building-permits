web: pipenv run gunicorn 'service.microservice:start_service()'
celery_beat: pipenv run celery -A tasks beat --loglevel=info