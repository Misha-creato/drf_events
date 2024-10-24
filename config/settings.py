"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
import sys
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 'django-insecure-u_0ss5&zl%5%-alrcky&07_d9ce@b#hd194!8(ly6(penql$by'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get(
    'DEBUG', 'True'
)
DEBUG = DEBUG == 'True'

HOST = os.environ.get(
    'HOST', '127.0.0.1',
)

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS', f'localhost, {HOST}'
).replace(' ', '').replace('|', '').split(',')

AUTH_USER_MODEL = 'users.CustomUser'

# CSRF

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1',
]
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1',
]

# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'solo',
    'drf_spectacular',
    'django_filters',
]

PROJECT_APPS = [
    'users',
    'notifications',
    'events',
    'tickets',
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DB_NAME = os.environ.get(
    'DB_NAME', 'events'
)
DB_USER = os.environ.get(
    'DB_USER', 'test_user'
)
DB_PASSWORD = os.environ.get(
    'DB_PASSWORD', '123456'
)
DB_HOST = os.environ.get(
    'DB_HOST', 'localhost'
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': '5432',
    }
}

# DRF

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.CustomJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# JWT

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}


# Redis

REDIS_PORT = os.environ.get(
    'REDIS_PORT', '6379'
)

REDIS_HOST = os.environ.get(
    'REDIS_HOST', '127.0.0.1'
)


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Asia/Almaty'

USE_I18N = True

USE_TZ = True

TZ_FOR_PAYMENT = '+05:00'

# Site

SITE_PROTOCOL = os.environ.get(
    'SITE_PROTOCOL', 'http'
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Email settings

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get(
    'EMAIL_HOST', 'smtp.gmail.com'
)
EMAIL_HOST_USER = os.environ.get(
    'EMAIL_HOST_USER', 'example@gmail.com'
)
EMAIL_HOST_PASSWORD = os.environ.get(
    'EMAIL_HOST_PASSWORD', 'password'
)
EMAIL_PORT = os.environ.get(
    'EMAIL_PORT', 587
)
EMAIL_USE_TLS = True


# Fixtures

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'apps', 'notifications', 'tests', 'fixtures'),
    os.path.join(BASE_DIR, 'apps', 'events', 'tests', 'fixtures'),
    os.path.join(BASE_DIR, 'apps', 'tickets', 'tests', 'fixtures'),
)

# Celery

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_TIMEZONE = 'Asia/Almaty'

# PAYMENT API
PAYMENT_HOST = os.environ.get(
    'PAYMENT_HOST', ''
)
PAYMENT_SITE_ID = os.environ.get(
    'PAYMENT_SITE_ID', ''
)
PAYMENT_AUTHORIZATION_TOKEN = os.environ.get(
    'PAYMENT_AUTHORIZATION_TOKEN', ''
)


# Google OAUTH:

CLIENT_ID = os.environ.get(
    'CLIENT_ID', ''
)
CLIENT_SECRET = os.environ.get(
    'CLIENT_SECRET', '',
)