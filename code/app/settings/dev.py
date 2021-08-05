from . import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

DEBUG = True
SECRET_KEY = 'just a dev key'
ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
