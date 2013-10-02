# Django settings for api project.
import sys
from sandbox_config import *

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('PennApps', 'pennappslabs@google.groups.com'),
)
SERVER_EMAIL="pennapps@ve.rckr5ngx.vesrv.com"

MANAGERS = ADMINS

# Values for DATABASE_NAME:
# 'coursesapi-v3-prod' - production (for now)
# 'coursesapi-v3-dev' - shared development
# whatever - your personal database, if you have one

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # 'django.db.backends.sqlite3' if 'test' in sys.argv else 'django.db.backends.mysql',
        # see sandbox_config.py
        'NAME': DATABASE_NAME,                      # Or path to database file if using sqlite3.
        'USER': DATABASE_USER,                      # Not used with sqlite3.
        'PASSWORD': DATABASE_PWD,                   # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 2

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''


# The absolute path to the Unix folder where ./manage.py collectstatic will
# deposit the symlinked static files
STATIC_ROOT = os.path.join(COURSESAPI_APP_ROOT, 'api/static')

# The actual URL from which static files are served.
# Examples: "http://foo.com/static/"
STATIC_URL = os.path.join(DISPLAY_NAME, 'static/')

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'F2g3XtfUb76T5g-PWNdIKYeD4ajuvz6tVLrDQLVddw5hVr7bnVGygYNUrYWGCNYs1'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'api.apiconsumer.authenticate.Authenticate',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    COURSESAPI_APP_ROOT + '/api/templates',
    COURSESAPI_APP_ROOT + '/api/cms/templates',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

STATICFILES_DIRS = (
    COURSESAPI_APP_ROOT + '/api/cms/static',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'api.courses',
    'api.apiconsumer',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'api.static_content',
    'api.cms',
    'django_extensions', # used for debugging, remove if problematic
    # 'django.contrib.staticfiles',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.staticfiles',
    'api.cms',
    # 'django.contrib.admindocs',
    'south',
)

#AUTHENTICATION_BACKENDS = 'tokenapi.backends.TokenBackend'

# Caching
if DO_CACHING:
    timeout_hours = 24*7
    CACHES = {
        'default': {
            'BACKEND': "django.core.cache.backends.filebased.FileBasedCache",
            # The directory in LOCATION should be owned by user: www-data
            'LOCATION': COURSESAPI_APP_ROOT + "/CACHES/current",
            'TIMEOUT': 60*60*timeout_hours # now in seconds
            }
        }


if USE_DJANGO_DEBUG_TOOLBAR:
    #MIDDLEWARE_CLASSES = tuple(c for c in MIDDLEWARE_CLASSES if "Authenticate" not in c)
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    INSTALLED_APPS += ('debug_toolbar',)
    wifi_3913 = '76.124.117.94'
    INTERNAL_IPS = (wifi_3913,'158.130.103.7')
