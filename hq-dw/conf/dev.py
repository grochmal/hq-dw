'''
Settings for the development environment.

These settings store database passwords in clear text.  Modify this file if the
database server you're connecting to can be acessed from outside a NAT!
'''

import os, sys
from .base import *

SECRET_KEY = 'aaaaaabbbbbbccccccddddddeeeeeeffffffgggggghhhhhhii'

DEBUG = True
ALLOWED_HOSTS = []

# The app names need to be duplicated here because the development versions
# reside in their own repositories.
APP_REPOS = [
    'hq-stage'
,   'hq-warehouse'
,   'hq-hotel-mart'
]
APPS_DIR = os.path.join(BASE_DIR, '..', '..', 'hq-apps')
for app in APP_REPOS:
    sys.path.append(os.path.join(APPS_DIR, app))

DATABASES = {
    # The default database will hold all authentication
    # and session data, this way we do not need to
    # route all contrib django modules.
    'default' : {
        'NAME': 'dev_auth'
    ,   'ENGINE': 'django.db.backends.postgresql'
    ,   'USER': 'django'
    ,   'PASSWORD' : 'password'
    ,   'HOST' : 'localhost'
    ,   'PORT' : '5432'
    }
,   'warehouse': {
        'NAME': 'dev_warehouse'
    ,   'ENGINE': 'django.db.backends.postgresql'
    ,   'USER': 'django'
    ,   'PASSWORD' : 'password'
    ,   'HOST' : 'localhost'
    ,   'PORT' : '5432'
    }
,   'stage': {
        'NAME': 'dev_stage'
    ,   'ENGINE': 'django.db.backends.postgresql'
    ,   'USER': 'django'
    ,   'PASSWORD' : 'password'
    ,   'HOST' : 'localhost'
    ,   'PORT' : '5432'
    }
,   'hotel_mart': {
        'NAME': 'dev_stage'
    ,   'ENGINE': 'django.db.backends.postgresql'
    ,   'USER': 'django'
    ,   'PASSWORD' : 'password'
    ,   'HOST' : 'localhost'
    ,   'PORT' : '5432'
    }
}

