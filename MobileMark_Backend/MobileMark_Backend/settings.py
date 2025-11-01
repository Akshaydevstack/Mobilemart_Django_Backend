"""
Django settings for MobileMark_Backend project.
"""

from pathlib import Path
import os
from datetime import timedelta

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------
# 🔹 Environment control
# -------------------------------------------------
DEBUG = False  # ✅ Change to False for production

if DEBUG:
    ENVIRONMENT = "local"
else:
    ENVIRONMENT = "production"

print(f"✅ Django is running in: {ENVIRONMENT.upper()} mode")

# -------------------------------------------------
# 🔹 Common settings
# -------------------------------------------------
SECRET_KEY = 'django-insecure-hww4)5)52)h*_b3ipu@6%4_x#_y836zt-&42hq*i*nkcg=g1s*'

ALLOWED_HOSTS = [
    '13.203.202.165',
    'ec2-13-203-202-165.ap-south-1.compute.amazonaws.com',
    'localhost',
    '127.0.0.1',
    'https://moble-mart.vercel.app/',
    "mobilemart.online",
    "www.mobilemart.online",
]

# -------------------------------------------------
# 🔹 Installed apps & middleware
# -------------------------------------------------
INSTALLED_APPS = [
    'users.apps.UsersConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    "channels",
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'products',
    'brands',
    'cart',
    'wishlist',
    'orders',
    'payments',
    'coupons',
    'common',
    'notifications.apps.NotificationsConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MobileMark_Backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'MobileMark_Backend.wsgi.application'
ASGI_APPLICATION = "MobileMark_Backend.asgi.application"

# -------------------------------------------------
# 🔹 Database Config (auto switch)
# -------------------------------------------------
if ENVIRONMENT == "local":
    print("✅ Using LOCAL PostgreSQL configuration")
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', # PostgreSQL backend
        'NAME': 'mobile_mart',             # Database name
        'USER': 'postgres',                 # Database username
        'PASSWORD': '12345678',             # Database password
        'HOST': 'localhost',                # Database host (use IP or domain if remote)
        'PORT': '5433',                     # Default PostgreSQL port
    }
}
    
else:
    print("✅ Using PRODUCTION RDS configuration")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'MobileMartAdmin',
            'PASSWORD': 'ztKV^Wj?2j.4)(j',
            'HOST': 'mobilemart-db.cv82ck8gae2y.ap-south-1.rds.amazonaws.com',
            'PORT': '5432',
        }
    }

# -------------------------------------------------
# 🔹 Password validation
# -------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------
# 🔹 Internationalization
# -------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------
# 🔹 Static & Media files
# -------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -------------------------------------------------
# 🔹 Authentication
# -------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "users.User"

# -------------------------------------------------
# 🔹 REST Framework
# -------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# -------------------------------------------------
# 🔹 JWT Config
# -------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# -------------------------------------------------
# 🔹 CORS & CSRF (Auto switch for local/production)
# -------------------------------------------------
if ENVIRONMENT == "production":
    print("✅ Using PRODUCTION CORS & COOKIE settings")

    CORS_ALLOWED_ORIGINS = [
        "https://moble-mart.vercel.app",
    ]
    CORS_ALLOW_CREDENTIALS = True

    CSRF_TRUSTED_ORIGINS = [
        "https://moble-mart.vercel.app",
    ]

    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = "None"
    CSRF_COOKIE_SECURE = True

else:
    print("✅ Using LOCAL CORS & COOKIE settings")

    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    CORS_ALLOW_CREDENTIALS = True

    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SECURE = False

# -------------------------------------------------
# 🔹 Email
# -------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'akshay.devstack@gmail.com'
EMAIL_HOST_PASSWORD = 'lefaxaqcbjxhifgy'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# -------------------------------------------------
# 🔹 Payment & Google
# -------------------------------------------------
GOOGLE_CLIENT_ID = "452036882317-m55vuhdiqaqmcjeal86aitpadnnrgc4b.apps.googleusercontent.com"
RAZORPAY_KEY_ID = "rzp_test_RVoZd9UTCaOnZS"
RAZORPAY_KEY_SECRET = "aktv2nzGgtHZHtxmgJXz3ewY"

# -------------------------------------------------
# 🔹 Channels (WebSocket)
# -------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}