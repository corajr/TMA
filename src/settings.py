import os
import sys
import pdb    
import shutil
# user limits and settings
MAX_UPLOAD_SIZE = 20 # in MB
MAX_WWW_DL_SIZE = 100 # in MB
MAX_WWW_FS = 5 # max filesize in MB
REMOVE_DWNLD = True # delete the downloaded content after processing
MAX_NUM_TERMS = 5000
MAX_NUM_TOPICS = 200
ALLOW_PERPLEX = True # enable perplexity analysis
TM_RUNTIME_LIMIT = 10000000 # maximum runtime in seconds (default = 115 days)

# Django settings
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# set up appropriate paths
SRC_PATH = os.path.realpath(os.path.dirname(__file__))
TRUNK_PATH = os.path.realpath(os.path.join(SRC_PATH,'../'))
WORKDIR = os.path.join(TRUNK_PATH, 'tmaout')
DATA_DIR = os.path.join(TRUNK_PATH,'data')
DEFAULT_STOP_WORDS = os.path.join(SRC_PATH,'backend/aux/stop_words.txt') # TODO add default stop-word file location to user settings

# add the trunk location to the pythonpath
sys.path.append(TRUNK_PATH)
sys.path.append(os.path.join(TRUNK_PATH, 'lib'))

# set up appropriate algorithms TODO make sure algorithms are installed correctly
ALG_LOCS = {
    'lda':os.path.join(TRUNK_PATH, 'lib/lda-c-dist'),
    'hdp':os.path.join(TRUNK_PATH, 'lib/hdp'),
    'ctm':os.path.join(TRUNK_PATH, 'lib/ctm-dist'),
    'dtm':os.path.join(TRUNK_PATH, 'lib/dtm_release/dtm')
}

# read personal settings
usettings = {}
sett_file = os.path.join(TRUNK_PATH, 'user-settings.txt')
if not  os.path.exists(sett_file):
    shutil.copy(os.path.join(TRUNK_PATH,'user-settings-TEMPLATE.txt'), sett_file)
with open(sett_file, 'r') as usetts:
    for line in usetts:
        splt = line.strip().split(':')
        usettings[splt[0].strip()] = ':'.join(splt[1:]).strip()

# Set wikipedia cooccurence database location TODO set a flag that determines whether user has database
WIKI_COCC_DB = os.path.join(DATA_DIR,'wiki_cocc_100percent.sqlite') # TODO: move this somewhere else?
WIKI_NUM_ABST = 3925809 # hardcoded number of abstracts in wiki database 

# bing api key, make sure to set in user-settings.txt
BING_API_KEY = usettings['bing-api-key']
                       
# django secret key (used for hashing), change the default in user-settings.txt
SECRET_KEY = usettings['django-secret-key']

# set admin in user-settings.txt
ADMINS = (
     (usettings['name'], usettings['email']),
)
MANAGERS = ADMINS

# TODO add cache setting here and/or in personal settings
# see https://docs.djangoproject.com/en/dev/topics/cache/ for params for the cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(WORKDIR, 'django_cache' ),
        'TIMEOUT': 60, 
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
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
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_ROOT = os.path.join(SRC_PATH, 'media')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(SRC_PATH, 'media/static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    ('css',os.path.join(SRC_PATH, 'staticfiles/css')),
    ('images',os.path.join(SRC_PATH, 'staticfiles/images')),
    ('js',os.path.join(SRC_PATH, 'staticfiles/js'))
		
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

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
)

ROOT_URLCONF = 'src.urls'

TEMPLATE_DIRS = (
    os.path.join(SRC_PATH,'templates/')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'endless_pagination',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
) 

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)
# For endless pagination
TEMPLATE_CONTEXT_PROCESSORS += (
     'django.core.context_processors.request',
)


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
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
