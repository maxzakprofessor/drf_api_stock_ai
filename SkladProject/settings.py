import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url  # 🔥 ДОБАВЬ ЭТУ СТРОКУ


# 1. ЗАГРУЗКА СЕКРЕТОВ (Открываем сейф 🔐)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

# ЧИТАЕМ ПЕРЕМЕННЫЕ ИЗ .ENV
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'

# --- СПИСОК ПРИЛОЖЕНИЙ ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # СТОРОННИЕ БИБЛИОТЕКИ
    'rest_framework',      
    'corsheaders',         
    'StockApp',            
]

# --- ПРОМЕЖУТОЧНОЕ ПО (MIDDLEWARE) ---
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
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}


# Пытаемся взять URL базы из переменной окружения (для Koyeb)
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # --- ОБЛАКО (Neon.tech) ---
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    # --- ЛОКАЛЬНО (Твой Postgres) ---
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sklad_db',      # Убедись, что создал её: CREATE DATABASE sklad_db;
        'USER': 'postgres',
        'PASSWORD': 'Sc0da3!',   # Твой новый сброшенный пароль 🦾
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
    }


# --- ИНТЕРНАЦИОНАЛИЗАЦИЯ ---
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- СТАТИЧЕСКИЕ ФАЙЛЫ ---
STATIC_URL = 'static/'
# 🔥 ДОБАВЬ ЭТУ СТРОКУ НИЖЕ
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

# Также проверь, что у тебя импортирован os в начале файла


# --- JWT (АВТОРИЗАЦИЯ) ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer', 'Token'), 
}

# --- СЕТЕВЫЕ НАСТРОЙКИ (CORS & HOSTS) ---
ALLOWED_HOSTS = [
    'mzakiryanovgmailcom.pythonanywhere.com', 
    'localhost', 
    '127.0.0.1',
    '.onrender.com',
    '.koyeb.app',  # 🔥 ДОБАВИЛИ ЭТУ СТРОКУ
    '*',           # 🔑 МОЖНО ДОБАВИТЬ ЗВЕЗДОЧКУ ДЛЯ 100% ГАРАНТИИ
]



CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",          
    "http://127.0.0.1:5173",
    "http://localhost:4200",
    "https://vue-api-stock.vercel.app", 
    "https://angular-api-sklad.vercel.app", 
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://angular-api-sklad.vercel.app",

]

CORS_ALLOW_HEADERS = [
    "accept",
    "authorization", 
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# --- ПОЧТОВЫЙ СЕРВЕР (Скрыт в .env 🛡️) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# --- МОНГО (АУДИТ) ---
MONGO_URI = os.getenv('MONGO_URI', "mongodb://localhost:27017/")
MONGO_DB_NAME = "sklad_audit_db"

# --- ФИКС CORS ДЛЯ VERCEL ---
APPEND_SLASH = False # 🚫 Отключаем редиректы, которые убивают CORS-заголовки
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]