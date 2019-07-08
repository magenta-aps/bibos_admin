# Django settings for bibos_admin project.

import os
from getenv import env

install_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)


DEBUG = env('DEBUG')
TEMPLATE_DEBUG = DEBUG

ADMINS = env('ADMINS')

MANAGERS = ADMINS


# Template settings
# Added because "TemplateDoesNotExist" error in Django 1.11
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':
        [
            os.path.join(install_dir, 'templates/')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors':
            [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


SOURCE_DIR = os.path.abspath(os.path.join(install_dir, '..'))

DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE'),
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': env('DB_NAME'),
        # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': '',
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = env('TIME_ZONE')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = env('LANGUAGE_CODE')

LOCALE_PATHS = [
    os.path.join(install_dir, 'locale')
]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(install_dir, 'site_media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = env('SECRET_KEY')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Email settings

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
ADMIN_EMAIL = env('ADMIN_EMAIL')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ROOT_URLCONF = 'bibos_admin.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'bibos_admin.wsgi.application'

# Don't forget to use absolute paths, not relative paths.
DOCUMENTATION_DIR =  os.path.join(install_dir, 'templates')


LOCAL_APPS = (
    'system',
    'account',
)

THIRD_PARTY_APPS = (
    'django_xmlrpc',
)

DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

XMLRPC_METHODS = (
    ('system.rpc.register_new_computer', 'register_new_computer'),
    ('system.rpc.send_status_info', 'send_status_info'),
    ('system.rpc.upload_dist_packages', 'upload_dist_packages'),
    ('system.rpc.get_instructions', 'get_instructions'),
    ('system.rpc.get_proxy_setup', 'get_proxy_setup'),
    ('system.rpc.push_config_keys', 'push_config_keys'),
    ('system.rpc.push_security_events', 'push_security_events')
)

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

AUTH_PROFILE_MODULE = 'account.UserProfile'

ETC_DIR = os.path.join(install_dir, 'etc')
PROXY_HTPASSWD_FILE = os.path.join(ETC_DIR, 'bibos-proxy.htpasswd')

# List of hosts that should be allowed through BibOS gateway proxies
DEFAULT_ALLOWED_PROXY_HOSTS = env('DEFAULT_ALLOWED_PROXY_HOSTS')

# List of hosts that should be proxied directly from the gateway and
# not through the central server
DEFAULT_DIRECT_PROXY_HOSTS = env('DEFAULT_DIRECT_PROXY_HOSTS')

CLOSED_DISTRIBUTIONS = env('CLOSED_DISTRIBUTIONS')
