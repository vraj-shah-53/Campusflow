import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load local environment variables from .env file if it exists
try:
    with open(os.path.join(BASE_DIR, '.env'), 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")
except Exception:
    pass



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(i#*06f#keydy_fh17bf=$0f6v)^wr^l7*u4gq42m*sztu#2_m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'campusflow-ucjm.onrender.com',
    'vgecw-ucjm.onrender.com',
    '.onrender.com',
    'https://campusflow-ucjm.onrender.com',
    'https://vgecw-ucjm.onrender.com',
]

RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
if RENDER_EXTERNAL_URL:
    CSRF_TRUSTED_ORIGINS.append(RENDER_EXTERNAL_URL)
    # Remove scheme for older Django 3.x
    clean_host = RENDER_EXTERNAL_URL.replace('https://', '').replace('http://', '')
    CSRF_TRUSTED_ORIGINS.append(clean_host)

CSRF_FAILURE_VIEW = 'student_management_app.views.custom_csrf_failure'

IS_RENDER = 'RENDER' in os.environ

if IS_RENDER:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    USE_X_FORWARDED_HOST = True
else:
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'student_management_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise Middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'student_management_app.LoginCheckMiddleWare.LoginCheckMiddleWare',
]

ROOT_URLCONF = 'student_management_system.urls'

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
                'student_management_app.context_processors.college_settings_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'student_management_system.wsgi.application'


# Database

PERSISTENT_DIR = os.environ.get('PERSISTENT_DIR')
if PERSISTENT_DIR:
    try:
        os.makedirs(PERSISTENT_DIR, exist_ok=True)
    except Exception:
        pass
    DB_PATH = os.path.join(PERSISTENT_DIR, 'db.sqlite3')
else:
    DB_PATH = os.path.join(BASE_DIR, 'db.sqlite3')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}


# Password validation

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


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# WhiteNoise Static File Storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'


# Media Files

MEDIA_URL = '/media/'

if PERSISTENT_DIR:
    MEDIA_ROOT = os.path.join(PERSISTENT_DIR, 'media')
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Custom USER

AUTH_USER_MODEL = "student_management_app.CustomUser"


# Custom Authentication Backend

AUTHENTICATION_BACKENDS = [
    'student_management_app.EmailBackEnd.EmailBackEnd'
]

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# --- FREE AI CHATBOT OPTIONS (No Credit Card Details Required) ---
# If you don't want to add credit card details for Google Gemini, you can use:
# 1. Groq (Get a free key from: https://console.groq.com/)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# 2. OpenRouter (Get a free key from: https://openrouter.ai/keys)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
