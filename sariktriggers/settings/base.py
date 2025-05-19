# sariktriggers/settings/base.py
import os
from pathlib import Path
from dotenv import load_dotenv

# --- Start Debug Prints ---
print(f"DEBUG: Attempting to load settings from base.py")
print(f"DEBUG: __file__ in base.py is: {__file__}")
# This is how your BASE_DIR is currently calculated
BASE_DIR_CALC = Path(__file__).resolve().parent.parent.parent
print(f"DEBUG: Calculated BASE_DIR in base.py is: {BASE_DIR_CALC}")

env_path_calc = BASE_DIR_CALC / ".env"
print(f"DEBUG: Calculated path for .env file is: {env_path_calc}")
print(f"DEBUG: Does .env file exist at calculated path? {env_path_calc.exists()}")
# --- End Debug Prints ---

# Original BASE_DIR and .env loading
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(env_path)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY_FROM_ENV = os.getenv("SECRET_KEY")

# --- Start Critical Check for SECRET_KEY ---
print(f"DEBUG: Value of SECRET_KEY from os.getenv(): '{SECRET_KEY_FROM_ENV}'")
if not SECRET_KEY_FROM_ENV:
    # If SECRET_KEY isn't found, Django will fail. Let's make it fail loudly here.
    raise ValueError(
        "CRITICAL SETTINGS ERROR: SECRET_KEY is not loaded from environment!"
        " Check .env file path and content."
    )
SECRET_KEY = SECRET_KEY_FROM_ENV
# --- End Critical Check ---
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",)
}
# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG will be set by prod.py or your .env for prod
DEBUG_FROM_ENV = os.getenv("DEBUG", "True").lower() in (
    "true",
    "1",
    "t",
)  # Default to True if not set for base
DEBUG = DEBUG_FROM_ENV
print(f"DEBUG: DEBUG in base.py set to: {DEBUG}")


# --- Corrected ALLOWED_HOSTS (schemes removed) ---
ALLOWED_HOSTS = [
    "5.223.47.56",
    "localhost",
    "127.0.0.1",
    "static.56.47.223.5.clients.your-server.de",
    # 'yourdomain.com', # If you have one
]
print(f"DEBUG: ALLOWED_HOSTS set to: {ALLOWED_HOSTS}")


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# --- Corrected CSRF_TRUSTED_ORIGINS (schemes for http, can include port if non-standard) ---
CSRF_TRUSTED_ORIGINS = [
    "5.223.47.56",  # Assuming default port 80 or handled by reverse proxy
    "static.56.47.223.5.clients.your-server.de",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
print(f"DEBUG: CSRF_TRUSTED_ORIGINS set to: {CSRF_TRUSTED_ORIGINS}")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "sheet_triggers",
    "rest_framework",
    "corsheaders",
    "actionapi",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sariktriggers.urls"
print(f"DEBUG: ROOT_URLCONF set to: {ROOT_URLCONF}")


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Ensure BASE_DIR used here is correct
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

WSGI_APPLICATION = "sariktriggers.wsgi.application"
# ... (rest of your base.py settings like DATABASES, etc.)
print("DEBUG: End of base.py parsing attempt.")
