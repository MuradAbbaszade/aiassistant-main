"""
Django settings for AI Assistant SaaS.
"""
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    AI_PROVIDER=(str, "mock"),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-only-ai-assistant-insecure-key-change-me")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Cloudflare / ngrok tunnels need HTTPS origins listed for POST forms (Knowledge Base, etc.)
_csrf_origins = env.list("CSRF_TRUSTED_ORIGINS", default=[])
_public = env("PUBLIC_BASE_URL", default="").strip().rstrip("/")
if _public and _public not in _csrf_origins:
    _csrf_origins.append(_public)
# Auto-trust Render / PUBLIC_BASE_URL hosts
from urllib.parse import urlparse

for _candidate in (
    _public,
    env("RENDER_EXTERNAL_URL", default="").strip().rstrip("/"),
    env("RENDER_EXTERNAL_HOSTNAME", default="").strip(),
):
    if not _candidate:
        continue
    _host = urlparse(_candidate if "://" in _candidate else f"https://{_candidate}").hostname
    if _host and _host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_host)
    if "://" in _candidate or _candidate.startswith("http"):
        _origin = _candidate
    elif "." in _candidate:
        _origin = f"https://{_candidate}"
    else:
        continue
    if _origin.startswith("http") and _origin not in _csrf_origins:
        _csrf_origins.append(_origin)

# Allow all Render subdomains when running on Render
if env("RENDER_EXTERNAL_HOSTNAME", default="") or env.bool("RENDER", default=False):
    if ".onrender.com" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(".onrender.com")

for _origin in ("http://127.0.0.1:8000", "http://localhost:8000"):
    if _origin not in _csrf_origins:
        _csrf_origins.append(_origin)
CSRF_TRUSTED_ORIGINS = _csrf_origins

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "core",
    "accounts",
    "businesses",
    "knowledge",
    "conversations",
    "leads",
    "ai",
    "channels",
    "analytics",
    "demo",
    "marketing",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "core.language_middleware.LanguageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.CurrentBusinessMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.tenant",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Render provides postgres://… — normalize for django-environ / Django
_default_sqlite = f"sqlite:///{(BASE_DIR / 'db.sqlite3').as_posix()}"
_database_url = (env("DATABASE_URL", default="") or "").strip().strip('"').strip("'")
if not _database_url:
    _database_url = _default_sqlite
if _database_url.startswith("postgres://"):
    _database_url = "postgresql://" + _database_url[len("postgres://") :]

try:
    DATABASES = {"default": env.db_url_config(_database_url)}
except Exception as exc:  # noqa: BLE001
    raise ImproperlyConfigured(
        "Invalid DATABASE_URL. On Render: Postgres → Info → copy Internal Database URL "
        f"into the web service env var DATABASE_URL. Parse error: {exc}"
    ) from exc

if not DATABASES["default"].get("ENGINE"):
    raise ImproperlyConfigured(
        "DATABASE_URL was set but no database ENGINE was detected. "
        "Use the full Internal Database URL from Render Postgres "
        "(starts with postgres:// or postgresql://)."
    )

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "az"
LANGUAGES = [
    ("az", "Azərbaycan"),
    ("en", "English"),
    ("ru", "Русский"),
]
TIME_ZONE = "Asia/Baku"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
if DEBUG:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_BUSINESS_ID = ""
DEMO_LOGIN_EMAIL = ""

AI_PROVIDER = env("AI_PROVIDER", default="mock")
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4o-mini")

# Instagram / Meta Messaging + OAuth
META_APP_ID = env("META_APP_ID", default="")
META_APP_SECRET = env("META_APP_SECRET", default="")
META_VERIFY_TOKEN = env("META_VERIFY_TOKEN", default="aikomekci_verify")
# Instagram Login app credentials (often same as Meta app, or from Instagram product panel)
INSTAGRAM_APP_ID = env("INSTAGRAM_APP_ID", default="")
INSTAGRAM_APP_SECRET = env("INSTAGRAM_APP_SECRET", default="")
INSTAGRAM_OAUTH_SCOPES = env(
    "INSTAGRAM_OAUTH_SCOPES",
    default="instagram_business_basic,instagram_business_manage_messages",
)
INSTAGRAM_REDIRECT_URI = env("INSTAGRAM_REDIRECT_URI", default="")
# Optional single-tenant fallback (prefer OAuth Channel tokens)
INSTAGRAM_ACCESS_TOKEN = env("INSTAGRAM_ACCESS_TOKEN", default="")
INSTAGRAM_ACCOUNT_ID = env("INSTAGRAM_ACCOUNT_ID", default="")
INSTAGRAM_API_HOST = env("INSTAGRAM_API_HOST", default="graph.instagram.com")
INSTAGRAM_GRAPH_VERSION = env("INSTAGRAM_GRAPH_VERSION", default="v21.0")
INSTAGRAM_BUSINESS_ID = env("INSTAGRAM_BUSINESS_ID", default="")
INSTAGRAM_FORCE_GRAPH_HOST = env.bool("INSTAGRAM_FORCE_GRAPH_HOST", default=True)
PUBLIC_BASE_URL = env("PUBLIC_BASE_URL", default="")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/onboarding/"
LOGOUT_REDIRECT_URL = "/"

SESSION_COOKIE_AGE = 60 * 60 * 24 * 14

SUPPORT_WHATSAPP = env("SUPPORT_WHATSAPP", default="994705550117")

# Email / OTP (leave EMAIL_HOST empty to use console + show OTP in UI when DEBUG)
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default=(
        "django.core.mail.backends.smtp.EmailBackend"
        if env("EMAIL_HOST", default="")
        else "django.core.mail.backends.console.EmailBackend"
    ),
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_TIMEOUT = env.int("EMAIL_TIMEOUT", default=8)  # seconds — prevents login hang on bad SMTP
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="AI Assistant <onboarding@resend.dev>")

# HTTPS email APIs (recommended on Render — SMTP is often blocked with Errno 101)
RESEND_API_KEY = env("RESEND_API_KEY", default="")
BREVO_API_KEY = env("BREVO_API_KEY", default="")
BREVO_SENDER_EMAIL = env("BREVO_SENDER_EMAIL", default="")
