# Django settings for api project.
import sys
import os

from sandbox_config import (DISPLAY_NAME, COURSESAPI_APP_ROOT, DO_CACHING,
                            DEBUG, DATABASE_NAME, DATABASE_USER, DATABASE_PWD,
                            SECRET_KEY, TEST_API_TOKEN,)

ADMINS = (
    ('PennApps', 'pennappslabs@google.groups.com'),
)
SERVER_EMAIL = "pennapps@ve.rckr5ngx.vesrv.com"

MANAGERS = ADMINS

DB_ENGINE = 'django.db.backends.sqlite3' if 'test' in sys.argv or DEBUG \
            else 'django.db.backends.mysql'

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "[::1]", "api.penncoursereview.com"]

DATABASES = {
    'default': {
        # sqlite3 is used when testing
        'ENGINE': DB_ENGINE,
        'NAME': DATABASE_NAME,  # Or path to database file if using sqlite3.
        'USER': DATABASE_USER,                      # Not used with sqlite3.
        'PASSWORD': DATABASE_PWD,                   # Not used with sqlite3.
        'HOST': '',  # Set to empty string for localhost. Not used with sqlite3
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    }
}

if DB_ENGINE.endswith("mysql"):
    DATABASES["default"]["OPTIONS"] = {
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
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

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'api.apiconsumer.authenticate.Authenticate',
)

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(COURSESAPI_APP_ROOT, '/api/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        }
    }
]

INSTALLED_APPS = (
    'corsheaders',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'api.courses',
    'api.apiconsumer',
    'api.static_content',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

CORS_ORIGIN_ALLOW_ALL = True

# Caching
if DO_CACHING:
    timeout_hours = 24 * 7
    CACHES = {
        'default': {
            'BACKEND': "django.core.cache.backends.filebased.FileBasedCache",
            # The directory in LOCATION should be owned by user: www-data
            'LOCATION': COURSESAPI_APP_ROOT + "/CACHES/current",
            'TIMEOUT': 60 * 60 * timeout_hours  # now in seconds
            }
        }


# Used for Django debug toolbar (or use debugsqlshell)
try:
    import debug_toolbar
except ImportError:
    pass
else:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    INSTALLED_APPS += ('debug_toolbar',)
    INTERNAL_IPS = ('158.130.103.7','127.0.0.1')
