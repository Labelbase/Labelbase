import os
from pathlib import Path

from configparser  import RawConfigParser

# Build paths inside the project like this: BASE_DIR / 'subdir'.
PROJECT_PATH = BASE_DIR = Path(__file__).resolve().parent.parent

proj_config = RawConfigParser()
try:
    assert proj_config.read('{}/config.ini'.format(PROJECT_PATH)) != []
except AssertionError:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Configuration file {}{} not found!".format(PROJECT_PATH, '/config.ini'))




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = proj_config.get('internal','secret_key')
CRYPTOGRAPHY_SALT = proj_config.get('internal','crypto_salt')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [ proj_config.get('internal','allowed_host')]


import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://3b833ae08ccc4ff68793e961fff4921c@o4504646963232768.ingest.sentry.io/4504646967361536",
    integrations=[
        DjangoIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
 #   'django.contrib.sessions',
    'user_sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'two_factor',

    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',

    'labelbase',
    'userprofile',
    'bootstrapform',
    'cryptography',

    'rest_framework',
    'rest_framework.authtoken',

    'sekizai',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'labellabor.urls'

LOGIN_URL = 'two_factor:login'

LOGIN_REDIRECT_URL = 'two_factor:profile'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_PATH, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
            ],
        },
    },
]

WSGI_APPLICATION = 'labellabor.wsgi.application'

TWO_FACTOR_REMEMBER_COOKIE_AGE = 60*60*24*14

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': proj_config.get('database', 'name'),
        'USER': proj_config.get('database', 'user'),
        'OPTIONS': {'charset': 'utf8mb4'},
        'PASSWORD': proj_config.get('database', 'password'),
        'HOST': proj_config.get('database', 'host'),
        'PORT': '',
    }
}

TWO_FACTOR_WEBAUTHN_RP_NAME = 'labelbase.space'

SESSION_ENGINE = 'user_sessions.backends.db'

REST_FRAMEWORK = { 'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema' }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-FILE_UPLOAD_HANDLERS 
FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.MemoryFileUploadHandler",
                        "django.core.files.uploadhandler.TemporaryFileUploadHandler"]
