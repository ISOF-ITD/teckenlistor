# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from signbank.settings.base import *
# settings.base imports settings_secret
# The following settings are defined in settings_secret:
# SECRET_KEY, ADMINS, DATABASES, EMAIL_HOST, EMAIL_PORT, DEFAULT_FROM_EMAIL

# ISOF extra:
PROJECT_NAME = '/teckenlistor'

# IMPORTANT: Debug should always be False in production
DEBUG = False

# IMPORTANT: The hostname that this signbank runs on, this prevents HTTP Host header attacks
# Is set in settings_secrets:
# ALLOWED_HOSTS = ['frigg-test.sprakochfolkminnen.se']

# A list of directories where Django looks for translation files.
LOCALE_PATHS = (
    '/var/www/django/teckenlistor/locale',
)

# The absolute path to the directory where collectstatic will collect static files for deployment.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = "/var/www/django/static"
# STATIC_ROOT = '/var/www/signbank/static/'
# This setting defines the additional locations the staticfiles app will traverse if the FileSystemFinder finder
# is enabled, e.g. if you use the collectstatic or findstatic management command or use the static file serving view.
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, "signbank", "static"),
)

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = '/var/www/django/media/'
# MEDIA_ROOT = '/var/www/signbank/media/'
# URL that handles the media served from MEDIA_ROOT, used for managing stored files.
# It must end in a slash if set to a non-empty value.
MEDIA_URL = '/media/'

# Within MEDIA_ROOT we store newly uploaded gloss videos in this directory
GLOSS_VIDEO_DIRECTORY = 'glossvideo'

# Location and URL for uploaded files.
UPLOAD_ROOT = MEDIA_ROOT + "upload/"
UPLOAD_URL = MEDIA_URL + "upload/"

# The backend to use for sending emails.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            # 'level': 'DEBUG',
            'propagate': False,
        },
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    }
}

# Turn on lots of logging
DO_LOGGING = False
LOG_FILENAME = "debug.log"

# This points to the wsgi.py file that is used in tools.py to make web server "reload" the application.
# WSGI_FILE = '/home/signbank/signbank-fi/signbank/wsgi.py'
WSGI_FILE = '/var/www/django/teckenlistor/signbank/wsgi.py'
