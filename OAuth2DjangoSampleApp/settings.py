"""
Django settings for OAuth2DjangoSampleApp project.

Generated by 'django-admin startproject' using Django 1.10.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', "4-q9i$$hhq-%ur9t=kpnpt5=eb=2j971t+$=buq^y0ngovj25b")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Django will always save session information to the database for every request
SESSION_SAVE_EVERY_REQUEST = True
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
ALLOWED_HOSTS = [
    '*'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'rest_framework',
    'django_filters',
    'requests',
    'sampleAppOAuth2',
    'UserCredentials',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'OAuth2DjangoSampleApp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "../sampleAppOAuth2/templates")
        ],
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

WSGI_APPLICATION = 'OAuth2DjangoSampleApp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config('ENGINE', "django.db.backends.sqlite3"),
        'NAME': os.path.join(BASE_DIR, str(config('DATABASE_NAME', "db.sqlite3"))),
    }
}

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %I:%M %p",
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': config('PAGE_SIZE', 10)
}
CRONJOBS = [
    ('*/59 * * * *', 'sampleAppOAuth2.jobs.synctask.sync_tasks')  # will create job after every 1 hour(59 mins)
]

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Karachi'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

LOGIN_URL = '/app/'
# QBO settings
"""
    CLIENT_ID = 'ABstuTDK6gdWfAESwdtSmROjh2u2TPSeHIYklXfYBYHW1304RR'
    CLIENT_SECRET = 'ylWZfmHkq7hRgxOGDNstIHB9g5fKSnba56tNEvxr'
    REDIRECT_URI = 'http://localhost:8000/app/authCodeHandler'
"""
DISCOVERY_DOCUMENT = 'https://developer.api.intuit.com/.well-known/openid_sandbox_configuration/'
GET_APP_SCOPES = ['com.intuit.quickbooks.accounting', 'openid', 'profile', 'email', 'phone', 'address']
SANDBOX_QBO_BASEURL = 'https://sandbox-quickbooks.api.intuit.com'
SANDBOX_PROFILE_URL = 'https://sandbox-accounts.platform.intuit.com/v1/openid_connect/userinfo'
ID_TOKEN_ISSUER = 'https://oauth.platform.intuit.com/op/v1'
# Procore Settings
"""
    ### PROD CREDENTIALS ###
    PROCORE_CLIENT_ID = "e06b71583731bde1bf99384ba33fb81acd4e434f354d34518c185c70041a1a07"
    PROCORE_CLIENT_SECRET = "8669b63b46a3809abd4b2ce4605036d194f50dfe691bdf0e9a7b996c7e0e4f32"
    PROCORE_REDIRECT_URI = "http://localhost:8000/app/users/home"
    
    ### SANDBOX CREDENTIALS ### 
    PROCORE_CLIENT_ID = "12f3628a2708a8a1515a71e19492f4330d9ca10032fcbbdad0ae8ba0a7394724"
    PROCORE_CLIENT_SECRET = "2caa74950d47cb0e06d97d2253d0b9e75eab33d65195adeab3bf1b09070d8d7e"
    PROCORE_REDIRECT_URI = "http://localhost:8000/app/users/home"
"""