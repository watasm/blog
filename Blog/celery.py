import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Blog.settings.local')
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Blog.settings.pro')

app = Celery('Blog')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'send-report-every-day': {
        'task': 'blog.tasks.send_mails',
        'schedule': crontab(day_of_month="*", hour=18),
    },
}
