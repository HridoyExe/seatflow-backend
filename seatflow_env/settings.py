from decouple import config
from pathlib import Path
from datetime import timedelta
from decouple import config
import cloudinary

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-2yw+7imm$cg4j8q6n7v1!=5zq79je+3whd#l9#_+%=clj+acqz'

# SECURITY WARNING: don't run with debug turned on in production!
CORS_ALLOW_ALL_ORIGINS = True
DEBUG = False
AUTH_USER_MODEL = 'accounts.User'
ALLOWED_HOSTS = ["localhost",".vercel.app",'127.0.0.1']


# Application definition

INSTALLED_APPS = [
    "corsheaders",
    "whitenoise.runserver_nostatic",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_spectacular',
    "phonenumber_field",
    'rest_framework',
    'djoser',
    'api',
    'accounts',
    'menu',
    'booking',
    'payment',
    "django_filters",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'seatflow_env.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'seatflow_env.wsgi.app'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
# Configuration  for cloudinary     
cloudinary.config(
    cloud_name=config('CLOUD_NAME', default=''),
    api_key=config('API_KEY', default=''),
    api_secret=config('API_SECRET', default=''),
    secure=True
)

#Media Storage Setting
DEFAULT_FILE_STORAGE='cloudinary_storage.storage.MediaCloudinaryStorage'
#For Supabase
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default=''),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "menu.pagination.CustomPagination",
    "PAGE_SIZE": 5,
    "COERCE_DECIMAL_TO_STRING": False,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'SeatFlow API',
    'DESCRIPTION': 'API documentation for SeatFlow project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_PATCH': True,
    'COMPONENT_PATH_EXTRACT_NAMES': True,
}

SIMPLE_JWT = {
   'AUTH_HEADER_TYPES': ('JWT',),
     "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
}
DJOSER = {
    'LOGIN_FIELD': 'email',
    'USER_ID_FIELD': 'id',
    'EMAIL_FRONTEND_PROTOCOL' : config('FRONTEND_PROTOCOL', default='http'),
    'EMAIL_FRONTEND_DOMAIN' : config('FRONTEND_DOMAIN', default='localhost:5173'),
    'EMAIL_FRONTEND_SITE_NAME' :"SeatFlow",
    'PASSWORD_RESET_CONFIRM_URL': 'reset-password/{uid}/{token}',
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True,
    'SERIALIZERS': {
        'current_user': 'accounts.serializers.AccountUserSerializer',
    },
}
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': "Authorization",
            'in': 'header',
            'description': "Enter Your JWT Token in the format: `JWT <your_token>`"
        }
    }
}
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE="whitenoise.storage.CompressedStaticFilesStorage"
MEDIA_ROOT = BASE_DIR / 'media'
BACKEND_URL = config('BACKEND_URL', default='http://localhost:8000')
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5173')

# SSL Commerz Settings
SSL_STORE_ID = config('SSL_STORE_ID', default='')
SSL_STORE_PASS = config('SSL_STORE_PASS', default='')
SSL_IS_SANDBOX = config('SSL_IS_SANDBOX', default=True, cast=bool)