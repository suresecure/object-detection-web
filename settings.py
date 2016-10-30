from kombu import Queue, Exchange
# SECRET_KEY = 'not_a_secret'
# BROKER_URL='amqp://client:client@192.168.3.71:5672//'
BROKER_URL='amqp://guest:guest@localhost:5672//'
# backend rpc will stuck
CELERY_RESULT_BACKEND='amqp://'
# CELERY_RESULT_PERSISTENT = False
CELERYD_CONCURRENCY = 2
# CELERYD_PREFETCH_MULTIPLIER = 1
# CELERY_ACKS_LATE = True
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Etc/UTC'

CELERY_QUEUES = (
    Queue(
        'important',
        exchange=Exchange('important'),
        routing_key="important",
        delivery_mode=1,
    ),
)
        # queue_arguments={'x-max-length': 50}
