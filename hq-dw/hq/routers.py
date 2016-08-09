'''
Database routers.

Since we are dealing with different databases routing the right models/tables
to the correct database aliases needs to be performed according to a mapping.
In essence, each app have its own database in the current configuration.
'''

# settings is not a module, therefore this won't work
# from django.conf.settings import DATABASE_MAPPING

from django.conf import settings
DATABASE_MAPPING = settings.DATABASE_MAPPING

class HqRouter(object):
    '''
    A Router that decides against which database a query happens.
    '''

    def db_for_read(self, model, **hints):
        # Read from the mapped db (if not mapped go to 'default')
        if model._meta.app_label in DATABASE_MAPPING:
            return DATABASE_MAPPING[model._meta.app_label]
        return None

    def db_for_write(self, model, **hints):
        # Write to the mapped db (if not mapped go to 'default')
        if model._meta.app_label in DATABASE_MAPPING:
            return DATABASE_MAPPING[model._meta.app_label]
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # Relations are only allowed in the same db
        db_obj1 = DATABASE_MAPPING.get(obj1._meta.app_label)
        db_obj2 = DATABASE_MAPPING.get(obj2._meta.app_label)
        if db_obj1 and db_obj2:
            if db_obj1 == db_obj2:
                return True
            else:
                return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Migrations shall only happen on the app's database
        if db in DATABASE_MAPPING.values():
            return db == DATABASE_MAPPING.get(app_label)
        elif app_label in DATABASE_MAPPING:
            return False
        return None

