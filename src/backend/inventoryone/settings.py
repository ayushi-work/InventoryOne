"""
Django settings for the InventoryOne Broker Web App.

Configuration is environment driven so the same image can run locally, in CI
and in production. Copy `.env.example` to `.env` to override defaults.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env(key, default=None):
    return os.environ.get(key, default)


def env_bool(key, default=False):
    return str(env(key, str(default))).strip().lower() in ("1", "true", "yes", "on")


def env_list(key, default=""):
    return [item.strip() for item in env(key, default).split(",") if item.strip()]


SECRET_KEY = env("DJANGO_SECRET_KEY", "django-insecure-dev-key-change-me-in-production")
DEBUG = env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "*" if DEBUG else "localhost,127.0.0.1")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'channels',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inventoryone.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'inventoryone.wsgi.application'
ASGI_APPLICATION = 'inventoryone.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("POSTGRES_DB", "inventoryone"),
        'USER': env("POSTGRES_USER", "ayushi"),
        'PASSWORD': env("POSTGRES_PASSWORD", ""),
        'HOST': env("POSTGRES_HOST", ""),
        'PORT': env("POSTGRES_PORT", ""),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = env("TZ", "Asia/Kolkata")
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = Path(env("MEDIA_ROOT", str(BASE_DIR / 'media')))

# Upload limits for KYC documents (10 MB).
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Object storage -------------------------------------------------------
# When AWS credentials are present, files are stored in S3; otherwise they are
# written to MEDIA_ROOT so the app still works out of the box.
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", "")
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", "")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", "ap-south-1")
AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", "")
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False

if AWS_STORAGE_BUCKET_NAME and AWS_ACCESS_KEY_ID:
    STORAGES = {
        'default': {'BACKEND': 'storages.backends.s3boto3.S3Storage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    }
else:
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    }

# --- Django REST Framework -------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': env('THROTTLE_ANON', '120/min'),
        'user': env('THROTTLE_USER', '1200/min'),
        'otp': env('THROTTLE_OTP', '10/min'),
    },
}

CORS_ALLOW_ALL_ORIGINS = env_bool('CORS_ALLOW_ALL_ORIGINS', DEBUG)
CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS', '')

# --- Channels (live inventory) --------------------------------------------
REDIS_URL = env("REDIS_URL", "redis://127.0.0.1:6379/0")
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [REDIS_URL]},
    },
}

# --- Celery ---------------------------------------------------------------
CELERY_BROKER_URL = env("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_TASK_ALWAYS_EAGER = env_bool('CELERY_TASK_ALWAYS_EAGER', True)
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

# --- Application specific -------------------------------------------------
# Echo the OTP back in the API response instead of emailing it.
OTP_DEBUG_MODE = env_bool('OTP_DEBUG_MODE', DEBUG)
OTP_TTL_MINUTES = int(env('OTP_TTL_MINUTES', '5'))

# Firebase Cloud Messaging (optional).
FCM_SERVER_KEY = env("FCM_SERVER_KEY", "")
FCM_ENDPOINT = env(
    "FCM_ENDPOINT", "https://fcm.googleapis.com/fcm/send")

# Google Maps (optional).
GOOGLE_MAPS_API_KEY = env("GOOGLE_MAPS_API_KEY", "")

# The frontend origin used for CORS in production.
FRONTEND_URL = env("FRONTEND_URL", "http://127.0.0.1:3000")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
