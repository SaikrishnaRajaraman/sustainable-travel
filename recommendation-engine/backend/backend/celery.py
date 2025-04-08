import os
from celery import Celery
from celery.signals import worker_ready

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['myapp'])

# Configure retry settings
app.conf.update(
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_connection_retry_delay=5,
    task_ignore_result=False,  # We want to store results
    task_store_errors_even_if_ignored=True,
    task_default_queue='celery',
    task_create_missing_queues=True,
    task_routes={
        'myapp.tasks.*': {'queue': 'celery'},
    },
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    broker_url=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
)

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

@worker_ready.connect
def at_start(sender, **kwargs):
    """Print a message when the worker starts."""
    print('Celery worker is ready!')