# Django settings for twit_bot project / more documentation to be written
import dj_database_url
import os
from kombu import Exchange, Queue
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))


def base(f=''):
    return os.path.join(BASE_DIR, f)


sys.path.insert(0, base('plugins'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {'default': dj_database_url.config()}

# project name
PACKAGE_NAMESPACE = 'djsocial'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*', ]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Kuwait'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = base('public_media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/public_media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = os.environ.get('STATIC_URL', '/static/')

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    base('public-assets'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get('SECRET_KEY', ')evz0)z+&*%=^ay(7$8yht687kz)shn*$w@0#_2w_#!h!-^t^k')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'apps.account.middleware.SocialAuthExceptionMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    base('templates')
)

# custom user model
AUTH_USER_MODEL = 'account.User'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'suit',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'storages',
    'south',
    'social_auth',
    'djcelery',
    'apps.extras',
    'apps.account',
    'apps.twitter',
)

#SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

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
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# context processor
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    "django.core.context_processors.request",
    # custom context processors
    'context_processor.load_settings',
)

# authentication backends
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TWITTER_EXTRA_DATA = [
    ('screen_name', 'screen_name'),
    ('user_info', 'user_info')
]

SOCIAL_AUTH_PIPELINE = (
    'apps.account.pipeline.social_auth_user',  # to handle is_active = False as suspended user
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'apps.account.pipeline.redirect_to_form',
    'apps.account.pipeline.set_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'apps.account.pipeline.update_email_validity',
    'apps.account.pipeline.set_user_details',
    'apps.account.pipeline.social_extra_data',
    'apps.account.pipeline.destroy_session_data',
)

SOCIAL_AUTH_ENABLED_BACKENDS = ('twitter',)

SOCIAL_AUTH_PARTIAL_PIPELINE_KEY = 'partial_pipeline'

# change from default serializers to pickle serializer
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# for django-orm-extensions to not conflict with south
SOUTH_DATABASE_ADAPTERS = {'default': 'south.db.postgresql_psycopg2'}

LOGIN_ERROR_URL = '/account/error/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'
SOCIAL_AUTH_BACKEND_ERROR_URL = '/account/error/'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False

MAX_SCHEDULED_ORDERS_PER_USER = 5

# boot-up celery
# Celery
import djcelery

djcelery.setup_loader()

CELERY_ENABLE_UTC = True
CELERY_DEFAULT_QUEUE = 'djsocial'
CELERY_QUEUES = (
    Queue('djsocial', Exchange('djsocial'), routing_key='djsocial'),
)

# Twitter settings
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET', '')
TWITTER_MAX_DAILY_TWEETS = 100
TWITTER_MAX_DAILY_RETWEET = 100
TWITTER_MAX_DAILY_FAV = 100
TWITTER_MAX_DAILY_FOLLOW = 10
TWITTER_MAX_DAILY_UNFOLLOW = 10

try:
    from settings.local_env import *
except ImportError:
    pass