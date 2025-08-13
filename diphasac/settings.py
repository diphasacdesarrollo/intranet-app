import os
from pathlib import Path
import dj_database_url
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-nyx9hscy!288rx=vty5(qotva4)h#zq&l8m7l5*b3s))n^lau="

DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL",
                         "postgresql://postgres:AXWtFgKphzKWydTnsqvVmFpMrjiaRBUG@junction.proxy.rlwy.net:37083/railway")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "web-production-e740.up.railway.app",
    "localhost",
    "127.0.0.1",
    "intranet.diphasac.com",
    "www.intranet.diphasac.com",
    "web-production-831c.up.railway.app",
]

# Application definition

INSTALLED_APPS = [
    'import_export',
    "whitenoise.runserver_nostatic",
    'main.apps.MainConfig',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware"
]

CSRF_TRUSTED_ORIGINS = [
    "https://web-production-e740.up.railway.app",
    "https://intranet.diphasac.com",
    "https://www.intranet.diphasac.com",
    "https://web-production-831c.up.railway.app",
]

ROOT_URLCONF = "diphasac.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'diphasac.jinja2.environment',
            "context_processors": [
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = "diphasac.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=1800)
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator", },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    # {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    # {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_L10N = True

USE_TZ = False

LOGOUT_REDIRECT_URL = '/'

LOGIN_REDIRECT_URL = '/iniciar-sesion'

LOGIN_URL = '/iniciar-sesion'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'diphasac'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_QUERYSTRING_AUTH = False

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ON_HEROKU = os.getenv("ON_HEROKU", 'False').lower() in ('true', '1', 't')

# Mailing config


SENDGRID_API_KEY = config("SENDGRID_API_KEY")


DEFAULT_FROM_EMAIL = 'Aclara Lab<no-reply@aclaralab.com>'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True

if ON_HEROKU:
    import django_heroku

    django_heroku.settings(locals(), databases=False)
    SECURE_SSL_REDIRECT = True
