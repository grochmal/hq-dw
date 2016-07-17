'''
Seetings using sqlite databases.

Sqlite databases are rather unreliable but good for quick hacks since python
supports them out of the box.

There are only two reasons you might want to use this environment:

*   You are on a machine without a compiler and without pgsql python bindings.
*   You are testing the database router (sqlite databases are quicker to clean
than postres databases).
'''

import os, sys
from .dev import *

DATABASES = {
    # The default database will hold all authentication
    # and session data, this way we do not need to
    # route all contrib django modules.
    'default' : {
        'NAME': os.path.join(BASE_DIR, 'db.default.sqlite3')
    ,   'ENGINE': 'django.db.backends.sqlite3'
    }
,   'warehouse': {
        'NAME': os.path.join(BASE_DIR, 'db.warehouse.sqlite3')
    ,   'ENGINE': 'django.db.backends.sqlite3'
    }
,   'stage': {
        'NAME': os.path.join(BASE_DIR, 'db.stage.sqlite3')
    ,   'ENGINE': 'django.db.backends.sqlite3'
    }
,   'hotel_mart': {
        'NAME': os.path.join(BASE_DIR, 'db.hotel_mart.sqlite3')
    ,   'ENGINE': 'django.db.backends.sqlite3'
    }
}

