"""
Django settings for Champions project.
World Cup 2026 Fantasy & Betting Platform.
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-champions-dev-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # Local apps
    'accounts',
    'core',
    'squad',
    'draft',
    'betting',
    'transfers',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'champions.urls'

TEMPLATES = [
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

WSGI_APPLICATION = 'champions.wsgi.application'

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# SimpleJWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# API-Football Configuration
API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY', '')
API_FOOTBALL_BASE_URL = 'https://v3.football.api-sports.io'

# Game Configuration - Tunable Parameters
GAME_CONFIG = {
    'STARTING_BUDGET': 10_000_000,
    'PLAYER_BASE_VALUE': 5_000_000,
    'POINTS_VALUE_MULTIPLIER': 500_000,
    'BENCH_POINTS_MULTIPLIER': 0.5,
    'ELIMINATION_COMPENSATION_RATE': 0.5,
    'SELL_PENALTY_RATE': 0.75,  # Get back 75% of value when selling
    'AUCTION_DURATION_HOURS': 12,
    'DRAFT_TIME_PER_PICK_SECONDS': 60,
    'SQUAD_SIZE': 16,
    'STARTING_XI_SIZE': 11,
    'OUTFIELD_SUBS': 3,
    'GK_SUBS': 1,
    'VALID_FORMATIONS': [
        '4-3-3', '4-4-2', '3-5-2', '3-4-3',
        '4-2-3-1', '4-5-1', '5-3-2', '5-4-1',
    ],
    'DEFAULT_FORMATION': '4-3-3',
    # World Cup 2026 API-Football IDs
    'WORLD_CUP_LEAGUE_ID': 1,  # FIFA World Cup
    'WORLD_CUP_SEASON': 2026,
}
