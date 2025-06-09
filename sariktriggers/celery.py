# sariktriggers/celery.py

import os

from celery import Celery
from dotenv import load_dotenv

# 2. CALL the function at the top to load your .env file
load_dotenv()

# 3. SET the default settings module (as we discussed before)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sariktriggers.settings.local")

app = Celery("sariktriggers")

# This line tells Celery to read its configuration from your Django settings.
# This will now work because load_dotenv() has made the secrets available.
app.config_from_object("django.conf:settings", namespace="CELERY")

# This line tells Celery to automatically find any tasks.py files in your apps.
app.autodiscover_tasks()
