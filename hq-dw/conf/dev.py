'''
Settings for the development environment.

These settings store database passwords in clear text.  Modify this file if the
database server you're connecting to can be accessed from outside a NAT, but do
not submit password to a code repository!
'''

import os, sys
from .base import *

SECRET_KEY = 'aaaaaabbbbbbccccccddddddeeeeeeffffffgggggghhhhhhii'

DEBUG = True
ALLOWED_HOSTS = []

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
        'NAME': 'dev_hotel_mart'
    ,   'ENGINE': 'django.db.backends.postgresql'
    ,   'USER': 'django'
    ,   'PASSWORD' : 'password'
    ,   'HOST' : 'localhost'
    ,   'PORT' : '5432'
    }
}

