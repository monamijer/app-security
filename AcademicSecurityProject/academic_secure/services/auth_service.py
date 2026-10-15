"""
Service d'authentification — VERSION SÉCURISÉE.
Corrige les faiblesses des missions 1.9, 1.13 et 1.14.
"""
from datetime import datetime, timedelta
from flask import current_app
from flask_login import login_user, logout_user
import jwt

from models import db
from models.user import User
from models.login_history import LoginHistory
from shared.academic_logic.helpers import get_client_ip, get_user_agent

MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 15


class AuthService:

    @staticmethod
    def authenticate(username: str, password: str) -> User | None:
        """Requête paramétrée + limitation des tentatives."""
        if not username or not password:
            AuthService._log(username or "", False, "missing_credentials")
            return None

        user = User.query.filter_by(username=username).first()

        if user and user.locked_until and user.locked_until > datetime.utcnow():
            AuthService._log(username, False, "account_locked")
            return None

        if not user or not user.check_password(password):
            if user:
                user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
                if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                    user.locked_until = datetime.utcnow() + timedelta(
                        minutes=LOCK_DURATION_MINUTES
                    )
                db.session.commit()
            AuthService._log(username, False, "bad_credentials")
            return None

        if not user.is_active:
            AuthService._log(username, False, "inactive")
            return None

        # Succès → reset compteurs
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user)
        AuthService._log(username, True, "OK")
        return user

    @staticmethod
    def logout():
        logout_user()

    @staticmethod
    def _log(username: str, success: bool, reason: str) -> None:
        try:
            db.session.add(LoginHistory(
                username_attempted=username[:80],
                ip_address=get_client_ip(),
                user_agent=get_user_agent(),
                success=success,
                reason=reason,
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()

    # --------- JWT strict ---------
    @staticmethod
    def generate_jwt(user: User) -> str:
        now = datetime.utcnow()
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.name if user.role else None,
            "iss": current_app.config["JWT_ISSUER"],
            "aud": current_app.config["JWT_AUDIENCE"],
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(hours=current_app.config["JWT_EXPIRATION_HOURS"]),
        }
        return jwt.encode(
            payload,
            current_app.config["JWT_SECRET_KEY"],
            algorithm="HS256",  # imposé
        )

    @staticmethod
    def decode_jwt(token: str) -> dict | None:
        try:
            return jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],  # jamais lu depuis le token
                issuer=current_app.config["JWT_ISSUER"],
                audience=current_app.config["JWT_AUDIENCE"],
                options={
                    "require": ["exp", "iat", "iss", "aud", "sub"],
                    "verify_exp": True,
                    "verify_iss": True,
                    "verify_aud": True,
                },
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None