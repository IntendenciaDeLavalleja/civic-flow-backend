import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# CivicFlow – Plataforma de Gestión Pública · IDL
# ─────────────────────────────────────────────────────────────────────────────


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def _parse_csv(
    value: str | None,
    fallback: tuple[str, ...],
) -> tuple[str, ...]:
    if not value:
        return fallback
    parsed = tuple(
        item.strip().lower()
        for item in value.split(',')
        if item.strip()
    )
    return parsed or fallback


class Config:
    SECRET_KEY = (
        os.environ.get('SECRET_KEY')
        or 'change-me-in-production-please'
    )
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or os.environ.get('DATABASE_URI')
        or 'sqlite:///gvl.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = (
        os.environ.get('MAIL_DEFAULT_SENDER')
        or 'noreply@gvl.local'
    )

    # App identity
    APP_NAME = os.environ.get('APP_NAME', 'CivicFlow')
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://localhost:5173'

    # WTF / CSRF (admin HTML panel)
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or SECRET_KEY

    # Session security (admin HTML panel uses server-side sessions)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = not _as_bool(os.environ.get('FLASK_DEBUG'), default=False)
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour admin session

    # Redis (optional – for rate limiting)
    REDIS_URL = os.environ.get('REDIS_URL') or 'memory://'
    RATELIMIT_STORAGE_URI = (
        os.environ.get('RATELIMIT_STORAGE_URI')
        or REDIS_URL
    )

    # CORS
    CORS_ALLOWED_ORIGINS = [
        o.strip() for o in
        os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
        if o.strip()
    ]

    # Works module files
    WORKS_UPLOAD_DIR = (
        os.environ.get('WORKS_UPLOAD_DIR')
        or os.path.join(os.getcwd(), 'uploads', 'works')
    )
    WORKS_ALLOWED_DOCUMENT_MIME_TYPES = _parse_csv(
        os.environ.get('WORKS_ALLOWED_DOCUMENT_MIME_TYPES'),
        (
            'application/pdf',
            'application/msword',
            (
                'application/vnd.openxmlformats-'
                'officedocument.wordprocessingml.document'
            ),
            'application/vnd.ms-excel',
            (
                'application/vnd.openxmlformats-'
                'officedocument.spreadsheetml.sheet'
            ),
            'text/plain',
        ),
    )
    WORKS_ALLOWED_IMAGE_MIME_TYPES = _parse_csv(
        os.environ.get('WORKS_ALLOWED_IMAGE_MIME_TYPES'),
        (
            'image/webp',
            'image/jpeg',
            'image/png',
            'image/gif',
        ),
    )
    WORKS_ALLOWED_MIME_TYPES = (
        WORKS_ALLOWED_DOCUMENT_MIME_TYPES
        + WORKS_ALLOWED_IMAGE_MIME_TYPES
    )
    WORKS_MAX_FILE_SIZE = int(
        os.environ.get('WORKS_MAX_FILE_SIZE')
        or 2 * 1024 * 1024
    )


