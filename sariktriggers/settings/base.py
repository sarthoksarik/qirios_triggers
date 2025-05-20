# base.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent.parent
# env_path = BASE_DIR / ".env"
# print("Loading .env from:", env_path)
# load_dotenv(env_path)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


env_path = BASE_DIR / ".env"


load_dotenv(env_path)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")


ALLOWED_HOSTS = [
    "5.223.47.56",  # Keep the IP
    "localhost",
    "127.0.0.1",
    "static.56.47.223.5.clients.your-server.de",  # <-- ADD THIS
    # If you have a real domain name pointing to the IP, add it too:
    # 'yourdomain.com',
    # 'www.yourdomain.com',
]
CORS_ALLOW_ALL_ORIGINS = True  # 🚨 Not safe for production!

CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    "http://5.223.47.56",  # Keep the IP
    "http://static.56.47.223.5.clients.your-server.de",
    "http://localhost:5173",  # Vite development server
    "http://127.0.0.1:5173",  # Localhost access"
    # Add any other origins that need to make CSRF-protected requests
    # e.g., your production frontend URL
]

# X_FRAME_OPTIONS = "ALLOWALL"

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

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "sariktriggers.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",  # Use the PostgreSQL engine
        "NAME": "sariktriggers_db",  # Your DB name
        "USER": "qirios",  # Your DB user
        "PASSWORD": "wasabi",  # Your DB password (IMPORTANT: Load from env var in production!)
        "HOST": "127.0.0.1",  # Assumes DB is on the same server
        # Use '127.0.0.1' if 'localhost' doesn't work
        "PORT": "5432",  # Default PostgreSQL port (can often be left empty '' or '5432')
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Disable browsable API (optional)
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",)
}
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    # Path to the directory containing React's static assets (JS, CSS, etc.)
    # Example: If you upload build to /home/sarik/qirios_frontend_build
    # and assets are in /home/sarik/qirios_frontend_build/assets
    # "/home/sarik/qirios_frontend_build",  # For Vite
    # '/home/sarik/qirios_frontend_build/static', # For Create React App
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
