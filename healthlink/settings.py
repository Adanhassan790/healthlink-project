import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
if not DEBUG:
    ALLOWED_HOSTS.extend([
        'railway.app',
        '*.railway.app',
        '*.up.railway.app',  # Matches web-production-xxxx.up.railway.app
    ])

# Application definition
INSTALLED_APPS = [
    'jazzmin',  # Must be before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    
    # Local apps - startup must be first to run migrations
    'startup',
    'users',
    'appointments',
    'triage',
    'consultations',
    'messaging',
    'payments',
    'prescriptions',
    'notifications',
    'administration',
]
AUTH_USER_MODEL = 'users.CustomUser'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'healthlink.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration for efficient static file handling
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

WSGI_APPLICATION = 'healthlink.wsgi.application'

# Database configuration
import dj_database_url

# Use DATABASE_URL from Railway, fall back to SQLite for development
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Production: Use PostgreSQL from Railway
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Development: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Allow all origins in development, restrict in production
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS += os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if os.getenv('CORS_ALLOWED_ORIGINS') else []
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# M-Pesa Daraja API Settings (Read from environment variables)
MPESA_ENVIRONMENT = os.getenv('MPESA_ENVIRONMENT', 'sandbox')  # 'sandbox' or 'production'
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', '')
MPESA_BUSINESS_SHORTCODE = os.getenv('MPESA_BUSINESS_SHORTCODE', '')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', '')
MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL', 'http://localhost:8000/payments/mpesa/callback/')

# ============== EMAIL CONFIGURATION ==============
# Email backend selection based on environment
if DEBUG:
    # Development: Console backend (prints emails to stdout) or file-based
    EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
else:
    # Production: SMTP backend
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# SMTP Configuration (used in production)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False') == 'True'

# Default sender email address
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@healthlink.local')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

# Enable/disable email notifications
SEND_EMAIL_NOTIFICATIONS = os.getenv('SEND_EMAIL_NOTIFICATIONS', 'True' if not DEBUG else 'False') == 'True'

# CSRF configuration for production
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

if not DEBUG:
    # Add production domain and Railway domain
    CSRF_TRUSTED_ORIGINS += [
        'https://railway.app',
        os.getenv('RAILWAY_STATIC_URL', '').rstrip('/') if os.getenv('RAILWAY_STATIC_URL') else '',
    ]
    CSRF_TRUSTED_ORIGINS = [origin for origin in CSRF_TRUSTED_ORIGINS if origin]  # Remove empty strings

# Add any additional trusted origins from environment
if os.getenv('CSRF_TRUSTED_ORIGINS'):
    CSRF_TRUSTED_ORIGINS += os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

# ============== JAZZMIN ADMIN CONFIGURATION ==============
JAZZMIN_SETTINGS = {
    "site_title": "HealthLink",
    "site_header": "HealthLink",
    "site_brand": "",
    "site_logo": "/static/images/logo.png",
    "login_logo": "/static/images/logo.png",
    "welcome_sign": "Welcome to HealthLink Admin",
    "copyright": "HealthLink © 2026. All rights reserved.",
    
    # Theme configuration
    "use_google_fonts_cdn": True,
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    # UI Customization
    "custom_css": """
        .navbar-header {
            display: flex;
            flex-direction: column;
            justify-content: center;
            width: auto;
            min-height: 80px;
        }
        .navbar-brand {
            display: block;
            margin-bottom: 5px;
        }
        .navbar-text {
            display: block;
            margin: 0;
        }
    """,
    "custom_js": None,
    "show_ui_builder": False,
    
    # Search
    "search_show_get_queryset_enabled": False,
    
    # Icons
    "icons": {
        "auth": "fas fa-users",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "users.CustomUser": "fas fa-user-circle",
        "users.DoctorProfile": "fas fa-stethoscope",
        "users.PatientProfile": "fas fa-heart",
        "appointments.Appointment": "fas fa-calendar-check",
        "messaging.Conversation": "fas fa-comments",
        "messaging.Message": "fas fa-envelope",
        "messaging.VideoCall": "fas fa-video",
        "prescriptions.Prescription": "fas fa-prescription-bottle",
        "prescriptions.PrescriptionItem": "fas fa-pills",
        "payments.Payment": "fas fa-credit-card",
        "notifications.Notification": "fas fa-bell",
        "triage.TriageResult": "fas fa-stethoscope",
    },
    
    # Dashboard configuration
    "show_statistics_on_login_page": True,
    "environmental_graph": True,
    "list_filter_collapsed": False,
    
    # Order of apps
    "order_with_respect_to": [
        "users",
        "appointments",
        "messaging",
        "prescriptions",
        "payments",
        "notifications",
        "triage",
    ],
    
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "vertical_tabs",
        "auth.group": "vertical_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small": False,
    "footer_small": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-light",
    "accent": "accent-teal",
    "sidebar": "sidebar-dark-purple",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "united",
    "dark_mode_theme": "darkly",
    "button_cursor": "pointer",
    "pagination": {
        "default": 20,
        "20": 20,
        "50": 50,
        "100": 100,
        "200": 200,
    },
    "actions_sticky_top": True,
}

# ============== LOGGING CONFIGURATION ==============
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name}:{lineno} - {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {name} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'healthlink': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'users': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'appointments': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'triage': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}