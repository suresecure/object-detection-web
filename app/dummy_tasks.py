import os
import optparse
import settings
import celery
import logging
import time

the_celery = celery.Celery('tasks')
the_celery.config_from_object(settings)

@the_celery.task(name="tasks.object_detection_task", queue="important")
def object_detection_task(imgstream, secure_filename):
    print 'get task'
    # time.sleep(1)
    return 1

