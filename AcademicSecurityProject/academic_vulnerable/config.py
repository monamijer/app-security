import os
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    """Configuration volontairement permissive — usage pédagogique uniquement."""

    SECRET_KEY = os.getenv("SECRET_KEY", "insecure-dev-secret-key-change-me")

    # SQLite — fichier placé dans instance/
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///academic_vulnerable.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Sessions
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = False   # ⚠️ volontairement faible
    SESSION_COOKIE_SECURE = False     # ⚠️ HTTP
    SESSION_COOKIE_SAMESITE = None    # ⚠️ volontairement faible

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "insecure-jwt-secret-key")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS = 24

    # Uploads (⚠️ dans static/ = accessible directement)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "txt", "docx", "zip"}

    # Divers
    ITEMS_PER_PAGE = 10
    DEBUG = True