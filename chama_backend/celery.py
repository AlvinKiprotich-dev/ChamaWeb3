import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chama_backend.settings')

app = Celery('chama_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'send-contribution-reminders': {
        'task': 'chama.tasks.send_contribution_reminder',
        'schedule': 86400.0,  # Run daily (24 hours in seconds)
    },
    'cleanup-unconfirmed-contributions': {
        'task': 'chama.tasks.cleanup_unconfirmed_contributions',
        'schedule': 3600.0,  # Run hourly
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
