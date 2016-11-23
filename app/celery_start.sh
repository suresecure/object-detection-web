# start celery workers
export C_FORCE_ROOT=1
celery -A tasks.the_celery worker
