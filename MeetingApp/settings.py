"""
Django settings for MeetingApp project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

import environ
import dj_database_url
import django_heroku
import firebase_admin
from firebase_admin import credentials

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True)
)
# reading .env file
environ.Env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.environ.get('SECRET_KEY', 'SOME+RANDOM+BACKUPKEz9+3vnmjb0u@&w68t#5_e8s9-lbfhv-')
SECRET_KEY = env('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
print('DEBUG =', DEBUG)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.0.2.2']

ASGI_APPLICATION = "MeetingApp.routing.application"
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],

            # "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'storages',
    'token_auth',
    'events',
    'tickets',
    'chat',
    'channels',
    'realtime',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MeetingApp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'MeetingApp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'meeting_app_backend',
            'USER': 'postgres',
            'PASSWORD': '1qaz@WSX',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

    db_from_env = dj_database_url.config()
    DATABASES['default'].update(db_from_env)

    django_heroku.settings(locals())
    del DATABASES['default']['OPTIONS']['sslmode']


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static_cdn', 'static_root')
# STATIC_URL = '/static/'
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'MeetingApp/static'),
]
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

DEFAULT_FILE_STORAGE = 'MeetingApp.storage_backends.MediaStorage'

AUTH_USER_MODEL = 'token_auth.UserProfile'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

AUTHENTICATION_BACKENDS = ['token_auth.backends.EmailBackend']


# cred = credentials.Certificate(
#     {
#         "type": "service_account",
#         "project_id": "meetingapp-27f7e",
#         "private_key_id": "0436b77e71749af3c2d3fb055a125982c6321277",
#         "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDL08aBupOJ6jBT\nD6eFT04psDjgMnjr8ckJ9JBrKwJDIdELhMnmui6Qo/d42VQvPgtiFXH0H30ow6Gp\nO5jWZ/R41uATABIwOsPsEYYIFXkXINwuLsvGPT2ehN5Mo7T/4dgUf5qQ4ER9evO5\n9ppE5zoG74zVje/Z1MfiCyRxGPYEbvTdBlGScswdoL5Gvat584UFRzvqJ01ABaFe\neqjj+mCT5YEZO0ZyVSoGRiUVsTChuY+L8ESXA46Riu1SZQjqT7LPY0thVMOKmb3E\nDrglgiYUqP3IIQSzitu1ew3UMbeBBxpX3hcKY8FYjjUKGb+b7N9wy4aCz/xdoleG\niGj1ZTi3AgMBAAECggEADHAdfbuEI7cl88U3+vgrIOG41si9sEg025kQJwbQDVPg\njP9knEiVBtm6ndlFPD/6mdjZ91FK/4dqM6JU+6095RHXr2q8F81X0oc1n2pDO8us\nvY5SSQQu4NMWBz85XSDLx5Rx1JCa6iO5AIp+QRSLHSYJEtvY3Kx4KUcP/KBogtfW\nkeKwcY5lKIk3SdUVBB+Md5PD6O9wyRcqui+QduEywT3EP62w1iEb6CJb4V8nXXJf\ni8okkosT5u3GIXnhFatXyitJ6R4zVMX//N3N0gf+ghJqpaThjQTfIzWOW9zfWIIH\ne5D26x39dopqdo0NrR4ArFGCITjQWp2cW3a9TXx+IQKBgQDzeZG3vUsTE8hbxtU1\ny3Ei5Ld0fqQTrB/nC62/IHRuYb/k+w+n5ALsqIaPqCgv/8BJvDGzTRPDhB4BkNuN\n+97izfiSZUmsyXpnReGIy9Ftq0F4yoNDvQG3Y55968CeXC5pj74wROzYQ0Bb1wVI\n60AcsHJJjvUegkSDoy9aXqa8MwKBgQDWUBGQmV1e+hL7A3GFU3j5WxR/X59Hx7ml\nwLReDzU8jPXjkOkqrb4CZRR9Rh0oYnbT72L6/nml80COZYL3WZipwdJQ2Rxeg6/1\nRBeBMeLfMwLYaIWvbg8ZDGBG5M3JyDi12hIe12GR47BqRHidxzpYSlKuGyZNBQc+\n5mA6g0WNbQKBgFVCzzqOuUmW9eTdvjA2bAoSGgRbjM2uywU328JAdUVqSa7AFH1w\npW2GnoiUFG6qmwW3N5hYd4FSNMfLmHciKq01/8QUYDZ337tmh1JGPbKv9B9+m3UP\nLRixdAEYm71Y/o/M3Ic+u8oH0vPWWm1spGjniT4lJ8VlTOTkMmLtHmptAoGAHSZS\n3Uoe6xY0krPLMwlBgRkkVpbZAVhnJeZqIgkLgqrhnwxMyqNLHuREvy1UNfP+maEL\n43vNbAcEFtoz0BT9sMlOI/UD6M8clc2nLMluRFGZ53mABXaA0zVduwbP/swe+o0o\nvc0p1kAT9MBPb5ZzlyK00D2dHgi7DZEkMZE9WpkCgYAwPZxHErWAr6JowF0Mbl5i\nm35ypc88p8Dt4HKoTlzfZnBnHMDI1Ht5SCXVAsGztW0CMgkCwMDZxUWWJiS+EWJ0\n0huyjTnSqR/zpUurBCWm1zLt9JYZ0mvOXy5EFSWxDo6yodK8+oHtgoXV8jguT91a\nMGgDGz/owPBaBtRO9KOe+w==\n-----END PRIVATE KEY-----\n",
#         "client_email": "firebase-adminsdk-1imjv@meetingapp-27f7e.iam.gserviceaccount.com",
#         "client_id": "107183285939664806188",
#         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#         "token_uri": "https://oauth2.googleapis.com/token",
#         "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#         "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-1imjv%40meetingapp-27f7e.iam.gserviceaccount.com"
#     }
# )
# firebase_admin.initialize_app(cred)
