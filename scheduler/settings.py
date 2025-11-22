from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-^oqo0l8#95ch4uq2ddgkznm0%nzgnk*a)w1)p$owd6$os$ymtj"
DEBUG = True

INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Tvoj app
    "planner",
    "accounts.apps.AccountsConfig",  # ⬅️ ovako, s .apps
    # (NEMA allauth-a)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "scheduler.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],   # ⬅️ obavezno
        "APP_DIRS": True,                   # ⬅️ obavezno
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "scheduler.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "hr"
TIME_ZONE = "Europe/Zagreb"
USE_I18N = True
USE_TZ = True

# -------------------------------
# STATIKA (PWA traži /static/)
# -------------------------------
STATIC_URL = "/static/"

# ⬅️ NOVO: gdje se nalaze IZVORNE static datoteke u developmentu
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# ⬅️ NOVO: gdje collectstatic skuplja sve fajlove za produkciju
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth flow (bez allauth-a)
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# --- security / hosts ---
ALLOWED_HOSTS = [
    "*", 

]

# Za forme/login/logout preko IP-a (Django traži shemu + host, po potrebi i port)
CSRF_TRUSTED_ORIGINS = [
    "http://10.4.3.63",
    "http://10.4.3.63:8000",
]

# ⬅️ (Opcionalno za PWA kolačiće u standalone modu; ostavi ovako dok si na HTTP-u lokalno)
SESSION_COOKIE_SAMESITE = "Lax"
# Kad ideš na HTTPS u produkciji, dodaš i:
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
