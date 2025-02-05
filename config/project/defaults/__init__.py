"""
Django Settings for MyProject

This is the default settings file for a Django project.
Modify these settings according to your deployment environment.

Author: [Your Name or Team]
"""

from jestit.helpers import paths

# ---------------------------------------------------------------------
# BASE DIRECTORIES
# ---------------------------------------------------------------------
# Define the base directory of the project
BASE_DIR = paths.PROJECT_ROOT

# ---------------------------------------------------------------------
# SECURITY SETTINGS
# ---------------------------------------------------------------------
SECRET_KEY = "SETYOUROWNKEY"

DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

APPEND_SLASH = False

# ---------------------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'authit.middleware.jwt.JWTAuthenticationMiddleware'
]

# ---------------------------------------------------------------------
# URL CONFIGURATION
# ---------------------------------------------------------------------
ROOT_URLCONF = 'project.urls'

# ---------------------------------------------------------------------
# TEMPLATE SETTINGS
# ---------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

# ---------------------------------------------------------------------
# WSGI APPLICATION
# ---------------------------------------------------------------------
# WSGI_APPLICATION = 'project.wsgi.application'

# ---------------------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': paths.VAR_ROOT / 'db.sqlite3',
    }
}

# ---------------------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ---------------------------------------------------------------------
# STATIC & MEDIA FILES
# ---------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = paths.VAR_ROOT / "static"
SITE_STATIC_ROOT = paths.VAR_ROOT / "site_static"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_DIRS = [SITE_STATIC_ROOT]

# ---------------------------------------------------------------------
# DEFAULT PRIMARY KEY FIELD TYPE
# ---------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------
# LOGGING CONFIGURATION (Optional)
# ---------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': paths.LOG_ROOT / 'django_errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# ---------------------------------------------------------------------
# EMAIL SETTINGS (For Production)
# ---------------------------------------------------------------------
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.example.com")
# EMAIL_PORT = os.getenv("EMAIL_PORT", 587)
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "your-email@example.com")
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "your-email-password")

# ---------------------------------------------------------------------
# CACHING (Optional)
# ---------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-cache-key',
    }
}

# ---------------------------------------------------------------------
# SESSION CONFIGURATION
# ---------------------------------------------------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# ---------------------------------------------------------------------
# CSRF & SECURITY HEADERS (For Production)
# ---------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = ""
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
