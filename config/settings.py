from pathlib import Path
import os
import yaml

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1ul5xe8x8(af%r6n5%3tkeb(y!_bawh39yea!4kw$b#d90$7_@'

# SECURITY WARNING: don't run with debug turned on in production!
if os.getenv('GAE_APPLICATION', None):
    # 本番環境
    DEBUG = False
    ALLOWED_HOSTS = ['really-site-434214.dt.r.appspot.com']
else:
    # 開発環境
    DEBUG = True
    ALLOWED_HOSTS = ['*']
    with open(os.path.join(BASE_DIR, 'secrets', 'secret_dev.yaml')) as file:
        objects = yaml.safe_load(file)
        for object in objects:
            os.environ[object] = objects[object]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'livereload',
    'django.contrib.staticfiles',
    'mysite',
    'blog',
    'demo',
    'channels',
]

ASGI_APPLICATION = 'config.asgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'livereload.middleware.LiveReloadScript',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # templateの場所を指定する
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # どこでも通知のカウントが見れるよう設定する
                'config.context_processors.notification_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if os.getenv('GAE_APPLICATION', None):
    # 本番環境
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['DB_NAME'],
            'USER': os.environ['DB_USERNAME'],
            'PASSWORD': os.environ['DB_USERPASS'],
            'HOST': '/cloudsql/{}'.format(os.environ['DB_CONNECTION']),
        }
    }
else:
    #開発環境
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.mysql',
    #         'NAME': os.environ['DB_NAME'],
    #         'USER': os.environ['DB_USERNAME'],
    #         'PASSWORD': os.environ['DB_USERPASS'],
    #         'HOST': '127.0.0.1',
    #         'PORT' : '3306',
    #     }
    # }
    # sqlite3の設定
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# ----- static 設定項目

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ----- static 設定項目

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'mysite.User'

# ログインページ
LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/'

# ログアウトページ
LOGOUT_URL = '/logout/'

LOGOUT_REDIRECT_URL = '/login/'

# --------- massage tab with bootstrap alert class ---------------------
from django.contrib import messages
MESSAGE_TAGS = {
    messages.ERROR: 'rounded-0 alert alert-danger rounded-3',
    messages.WARNING: 'rounded-0 alert alert-warning rounded-3',
    messages.SUCCESS: 'rounded-0 alert alert-success rounded-3',
    messages.INFO: 'rounded-0 alert alert-info rounded-3',
    messages.DEBUG: 'rounded-0 alert alert-secondary rounded-3',
}
# --------- massage tab with bootstrap alert class ---------------------


# ----------- Gmail設定 --------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_OPERATION = os.environ['EMAIL_OPERATION']

# ----------- Gmail設定 --------------

# -----------キャッシュ ----------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}
# -----------キャッシュ ----------------