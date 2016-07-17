'''
Django base settings for the hq-dw project.

This file needs to be imported from the actual settings files.
'''

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# These three settings will make the boot fail if this file is used as the
# settings file, this is intended.  You need to overwrite them.
SECRET_KEY = None
DEBUG = False
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'hq_stage'
,   'hq_warehouse'
,   'hq_hotel_mart'
,   'django.contrib.admin'
,   'django.contrib.auth'
,   'django.contrib.contenttypes'
,   'django.contrib.sessions'
,   'django.contrib.messages'
,   'django.contrib.staticfiles'
]

DATABASE_MAPPING = {
    'hq_stage' : 'stage'
,   'hq_warehouse' : 'warehouse'
,   'hq_hotel_mart' : 'hotel_mart'
# all other apps fallback to the 'default' database
}

DATABASE_ROUTERS = [ 'hq.routers.HqRouter' ]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware'
,   'django.contrib.sessions.middleware.SessionMiddleware'
,   'django.middleware.common.CommonMiddleware'
,   'django.middleware.csrf.CsrfViewMiddleware'
,   'django.contrib.auth.middleware.AuthenticationMiddleware'
,   'django.contrib.auth.middleware.SessionAuthenticationMiddleware'
,   'django.contrib.messages.middleware.MessageMiddleware'
,   'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates'
    ,   'DIRS': []
    ,   'APP_DIRS': True
    ,   'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug'
            ,   'django.template.context_processors.request'
            ,   'django.contrib.auth.context_processors.auth'
            ,   'django.contrib.messages.context_processors.messages'
            ]
        }
    }
]

WSGI_APPLICATION = 'conf.wsgi.application'

# This will never work, overwrite it in a proper settings file.
DATABASES = { 'default': {} }

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME':
'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    }
,   { 'NAME':
      'django.contrib.auth.password_validation.MinimumLengthValidator'
    }
,   { 'NAME':
      'django.contrib.auth.password_validation.CommonPasswordValidator'
    }
,   { 'NAME':
      'django.contrib.auth.password_validation.NumericPasswordValidator'
    }
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

