import os
from celery import Celery
from celery.signals import after_setup_logger
import logging

# Set up the settings module of Django, and Celery will read the configuration information contained in this module.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OA_backend.settings')

# Create a Celery object
app = Celery('OA_backend')

# log management

@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add filehandler
    fh = logging.FileHandler('celery.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

# The configuration reads the Celery configuration information from settings.py. All Celery configuration information must start with "CELERY_". # broker_url: CELERY_BROKER_URL
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks. Tasks can be written in tasks.py.
app.autodiscover_tasks()


# Test Task
# 1. When bind=True, in the task function, the first parameter is the task object (Task). If this parameter is not set or bind=False, then there will be no task object parameter in the task function.
# 2. When ignore_result=True, the result of the task execution will not be saved.
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    # print(f'Request: {self.request!r}')
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxx")