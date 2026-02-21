"""
Django settings for SkladProject project.
"""

from pathlib import Path
from datetime import timedelta

# Основная директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# СЕКРЕТНЫЙ КЛЮЧ (Для разработки)
SECRET_KEY = 'django-insecure-=%zd97r-dh*yo0&u^3l000z08x0k3l=q7pt*nlkd+m9fxxx41u'

# Режим отладки (True — для разработки, False — для сервера)
DEBUG = True

# Список разрешенных хостов
ALLOWED_HOSTS = []

# --- СПИСОК ПРИЛОЖЕНИЙ ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # СТОРОННИЕ БИБЛИОТЕКИ
    'rest_framework',      # Инструментарий для создания API
    'corsheaders',         # Нужен, чтобы Vue мог делать запросы к Django (CORS)
    'StockApp',            # Ваше основное приложение склада
]

# --- ПРОМЕЖУТОЧНОЕ ПО (MIDDLEWARE) ---
MIDDLEWARE = [
    # CorsMiddleware должен быть ПЕРВЫМ в списке для работы запросов с фронтенда
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SkladProject.urls'

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

WSGI_APPLICATION = 'SkladProject.wsgi.application'

# --- БАЗА ДАННЫХ ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- ВАЛИДАЦИЯ ПАРОЛЕЙ ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- ИНТЕРНАЦИОНАЛИЗАЦИЯ ---
LANGUAGE_CODE = 'ru-ru' # Изменил на русский для удобства в админке
TIME_ZONE = 'UTC'       # Можно поставить 'Asia/Almaty' или ваш город
USE_I18N = True
USE_TZ = True

# Статические файлы
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# НАСТРОЙКИ ДЛЯ СВЯЗИ С VUE И АВТОРИЗАЦИИ (JWT)
# ==============================================================================

# Разрешаем запросы со всех адресов (для разработки)
CORS_ALLOW_ALL_ORIGINS = True 

# Автоматически добавлять слеш в конце URL (важно для Django)
APPEND_SLASH = True

# Глобальные настройки Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        # ВАЖНО: Эта настройка закрывает ВСЕ эндпоинты. 
        # Доступ будет только у авторизованных пользователей с токеном.
        'rest_framework.permissions.IsAuthenticated', 
    ],
}

# Настройки времени жизни токенов SimpleJWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # Токен живет 1 час
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    # Обновление сессии доступно сутки
    'ROTATE_REFRESH_TOKENS': False,
    # Типы заголовков, которые Vue будет слать в Authorization (Bearer <token>)
    'AUTH_HEADER_TYPES': ('Bearer', 'Token'), 
}

# 1. Выключаем полный доступ
CORS_ALLOW_ALL_ORIGINS = False

# 2. Разрешаем только твоему Vue-приложению
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",           # Твой локальный Vue (Vite) во время разработки
    "https://your-vue-app.netlify.app", # Адрес, где будет лежать твой фронтенд в сети
    "https://your-domain.com",         # Твой основной домен (если есть)
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://your-vue-app.netlify.app",
]
