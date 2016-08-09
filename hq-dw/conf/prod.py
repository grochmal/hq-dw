'''
Settings for production deployment.

Note that you need to set a couple of environment variables that should not be
openly known (e.g. do not upload the contents of the variables to a source
repository):

HQ_DW_SECRET_KEY: A byte string, can be anything but must remain secret.
HQ_DW_AUTH_NAME: The database user for the webserver database.
HQ_DW_AUTH_PASS: The password for the webserver database user.
HQ_DW_WAREHOUSE_NAME: Database user for the warehouse database.
HQ_DW_WAREHOUSE_PASS: Password for the warehouse user.
HQ_DW_STAGE_NAME: Database user for the stage database.
HQ_DW_STAGE_PASS: Password of the stage user.
HQ_DW_HOTEL_MART_NAME: Database user for the hotel data mart.
HQ_DW_HOTEL_MART_PASS: Password of the data mart user.

It is also likely that you will need to change ALLOWED_HOSTS to match your
domain.
'''

import os
from django.core.exceptions import ImproperlyConfigured
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['hqdw.grochmal.org']

env = {
    'HQ_DW_SECRET_KEY' : ''
,   'HQ_DW_AUTH_NAME' : ''
,   'HQ_DW_AUTH_PASS' : ''
,   'HQ_DW_WAREHOUSE_NAME' : ''
,   'HQ_DW_WAREHOUSE_PASS' : ''
,   'HQ_DW_STAGE_NAME' : ''
,   'HQ_DW_STAGE_PASS' : ''
,   'HQ_DW_HOTEL_MART_NAME' : ''
,   'HQ_DW_HOTEL_MART_PASS' : ''
}
def get_env():
    errors = []
    for k in env:
        data = os.environ.get(k, '')
        if not data:
            errors += ['You need to set the %s environment variable' % k]
        else:
            env[k] = data
    if [] != errors:
        raise ImproperlyConfigured('\n'.join(errors))

get_env()

SECRET_KEY = env['HQ_DV_SECRET_KEY']
DATABASES = {
    # The default database will hold all authentication
    # and session data, this way we do not need to
    # route all contrib django modules.
    'default' : {
        'NAME': 'prod_auth'
    ,   'ENGINE': 'django.db.backends.postgresql'
    ,   'USER': env['HQ_DW_AUTH_NAME']
    ,   'PASSWORD' : env['HQ_DW_AUTH_PASS']
    ,   'HOST' : 'localhost'
    ,   'PORT' : '5432'
    }
,   'warehouse': {
        'NAME': 'prod_warehouse'
    ,   'ENGINE': 'django.db.backends.postgresql'
    ,   'USER': env['HQ_DW_WAREHOUSE_NAME']
    ,   'PASSWORD' : env['HQ_DW_WAREHOUSE_PASS']
    ,   'HOST' : 'localhost'
    ,   'PORT' : '5432'
    }
,   'stage': {
        'NAME': 'prod_stage'
    ,   'ENGINE': 'django.db.backends.postgresql'
    ,   'USER': env['HQ_DW_STAGE_NAME']
    ,   'PASSWORD' : env['HQ_DW_STAGE_PASS']
    ,   'HOST' : 'localhost'
    ,   'PORT' : '5432'
    }
,   'hotel_mart': {
        'NAME': 'prod_hotel_mart'
    ,   'ENGINE': 'django.db.backends.postgresql'
    ,   'USER': env['HQ_DW_HOTEL_MART_NAME']
    ,   'PASSWORD' : env['HQ_DW_HOTEL_MART_PASS']
    ,   'HOST' : 'localhost'
    ,   'PORT' : '5432'
    }
}

