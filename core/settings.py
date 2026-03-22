import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# مفتاح الأمان
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-here')

# جعل DEBUG = False في الإنتاج أوتوماتيكياً
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# إعدادات الروابط المسموحة
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # المكتبات الأساسية لـ API
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    # تطبيق اللوجستيات
    'logistics',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # لخدمة الملفات الثابتة
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'core.wsgi.application'

# 🗄️ الربط الحقيقي بقاعدة بيانات السيرفر
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgres://koyeb-adm:npg_bIET6cGBLhv5@ep-old-band-ag4h5n6x.c-2.eu-central-1.pg.koyeb.app/koyebdb'
)

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = []

# إعدادات اللغة والوقت (مصر)
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# 📂 الملفات الثابتة (Static Files)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# المسار اللي ديجانجو هيدور فيه على ملف JS الباركود
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# استخدام WhiteNoise لخدمة الملفات المضغوطة
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 🖼️ ملفات الميديا (صور المنتجات)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# إعدادات الأمان (CORS & CSRF)
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = [
    'https://aksab.pythonanywhere.com',
    'https://*.koyeb.app'
]
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False

# إعدادات REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

