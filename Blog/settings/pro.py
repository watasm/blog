from .base import *

DEBUG = True

ADMINS = (
    ('Martin', 'martin.mkhitaryan2000@gmail.com'),

)
X_FRAME_OPTIONS = 'SAMEORIGIN'
# SECURE_SSL_REDIRECT = True
# CSRF_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SESSION_COOKIE_SECURE = True

# DATABASES = {
#     'default': {
#         'ENGINE': 'django_dbpool.db.backends.postgresql_psycopg2',
#         'NAME': 'blog',
#         'USER': 'blog',
#         'PASSWORD': 'fdsa1234',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }
# DATABASE_POOL_ARGS = {
#     'max_overflow': 10,
#     'pool_size': 5,
#     'recycle': 300
# }

DATABASES = {
    'default': {
        'ENGINE': 'django_mysql_geventpool.backends.mysql',
        'NAME': 'blog',
        'USER': 'blog',
        'PASSWORD': '$Fdsa1234$',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8',
            'use_unicode': True,
            'MAX_CONNS': 100,
            'MAX_LIFETIME': 5 * 60  # connection lifetime in seconds, and if set 0, unlimited persistent connections if usable. default is 0.
        }
    }
}
