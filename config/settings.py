"""Django settings for the ORIK Webcraft API.

Everything environment-specific is read from .env (see .env.example).
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


DEV_SECRET_KEY = "dev-only-insecure-key-change-me"


def env(name, default=""):
    """A blank value counts as unset, because .env.example ships keys empty."""
    return os.getenv(name, "").strip() or default


def env_bool(name, default=False):
    return env(name, str(default)).lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    return [item.strip() for item in env(name, default).split(",") if item.strip()]


# A placeholder keeps `runserver` working out of the box; production must set
# DJANGO_SECRET_KEY, and the check below refuses to start without it.
SECRET_KEY = env("DJANGO_SECRET_KEY", DEV_SECRET_KEY)
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

# Render injects the service's public hostname at runtime.
RENDER_HOSTNAME = env("RENDER_EXTERNAL_HOSTNAME")
if RENDER_HOSTNAME and RENDER_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_HOSTNAME)

if not DEBUG and SECRET_KEY == DEV_SECRET_KEY:
    raise RuntimeError("Set DJANGO_SECRET_KEY before running with DJANGO_DEBUG=False.")

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "enquiries",
    "content",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serves static files in production; Django itself will not with DEBUG=False.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # CORS must sit above CommonMiddleware so preflights get their headers.
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Render (and most hosts) provide a single DATABASE_URL. The POSTGRES_* vars
# stay supported for anyone wiring Postgres by hand; SQLite is the dev default.
if env("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.parse(
            env("DATABASE_URL"),
            conn_max_age=600,
            # Managed Postgres requires TLS; local docker instances do not.
            ssl_require=not DEBUG,
        )
    }
elif env("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_DB"),
            "USER": env("POSTGRES_USER"),
            "PASSWORD": env("POSTGRES_PASSWORD"),
            "HOST": env("POSTGRES_HOST", "localhost"),
            "PORT": env("POSTGRES_PORT", "5432"),
        }
    }
else:
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

LANGUAGE_CODE = "en-us"
TIME_ZONE = env("DJANGO_TIME_ZONE", "Asia/Kathmandu")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Compresses and fingerprints static files so they can be cached forever.
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Uploaded images (team portraits). In production serve these from the web
# server or object storage, not Django.
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    # The site is public and write-only; no sessions or tokens involved.
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_THROTTLE_RATES": {
        "enquiries": env("ENQUIRY_RATE_LIMIT", "5/hour"),
    },
}

if DEBUG:
    # Keeps the browsable API available while developing.
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append("rest_framework.renderers.BrowsableAPIRenderer")

# Only the site's own origins may call the API from a browser.
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001",
)
CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS"]

CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", ",".join(CORS_ALLOWED_ORIGINS))

if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# --- Jazzmin admin theme -----------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "ORIK Webcraft",
    "site_header": "ORIK Webcraft",
    "site_brand": "ORIK Webcraft",
    "welcome_sign": "ORIK Webcraft admin",
    "copyright": "ORIK Webcraft",
    "search_model": ["enquiries.Enquiry"],
    "topmenu_links": [
        {"name": "Enquiries", "model": "enquiries.Enquiry"},
        {"name": "View site", "url": env("SITE_URL", "http://localhost:3001"), "new_window": True},
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "enquiries.Enquiry": "fas fa-envelope-open-text",
        "content": "fas fa-pen-to-square",
        "content.HeroSection": "fas fa-star",
        "content.HeroBadge": "fas fa-certificate",
        "content.YourIdeaSection": "fas fa-lightbulb",
        "content.DigitalExperiencesSection": "fas fa-chart-simple",
        "content.IndustriesSection": "fas fa-store",
        "content.Template": "fas fa-layer-group",
        "content.SiteSettings": "fas fa-gear",
        "content.SocialLink": "fas fa-share-nodes",
        "content.Stat": "fas fa-chart-simple",
        "content.Problem": "fas fa-triangle-exclamation",
        "content.Industry": "fas fa-store",
        "content.Project": "fas fa-briefcase",
        "content.ProcessStep": "fas fa-list-ol",
        "content.Package": "fas fa-box-open",
        "content.Testimonial": "fas fa-quote-left",
        "content.FaqItem": "fas fa-circle-question",
        "content.TeamMember": "fas fa-user-group",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "changeform_format": "horizontal_tabs",
    # Naming models pins their sidebar order; anything unlisted follows, so the
    # hero sits above FAQs instead of falling into the alphabetical list.
    "order_with_respect_to": [
        "content",
        "content.HeroSection",
        "content.YourIdeaSection",
        "content.DigitalExperiencesSection",
        "content.IndustriesSection",
        "content.Industry",
        "content.Template",
        "content.FaqItem",
        "content.Package",
        "content.Project",
        "content.ProcessStep",
        "content.Problem",
        "content.Stat",
        "content.TeamMember",
        "content.Testimonial",
        "content.SiteSettings",
        "content.SocialLink",
        "enquiries",
        "auth",
    ],
    "show_ui_builder": False,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "navbar": "navbar-white navbar-light",
    "sidebar": "sidebar-dark-success",
    "brand_colour": "navbar-success",
    "accent": "accent-success",
    "button_classes": {
        "primary": "btn-success",
        "success": "btn-success",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
    },
    "sidebar_nav_flat_style": True,
    "actions_sticky_top": True,
}
