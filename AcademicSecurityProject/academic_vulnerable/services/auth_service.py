import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

"""
Service d'authentification — VERSION VULNÉRABLE.
Contient volontairement des faiblesses pour les missions 1.9 et 1.13.
"""
from datetime import datetime, timedelta
from flask import current_app
from flask_login import login_user, logout_user
import jwt

from models import db
from models.user import User
from models.login_history import LoginHistory
from shared.academic_logic.helpers import get_client_ip, get_user_agent


class AuthService:

    @staticmethod
    def authenticate(username: str, password: str) -> User | None:
        """
        ⚠️ Volontairement vulnérable : requête SQL par concaténation (Mission 1.9).
        NE PAS RÉUTILISER hors du laboratoire.
        """
        from sqlalchemy import text
        query = text(
            f"SELECT * FROM users WHERE username = '{username}' LIMIT 1"
        )
        try:
            row = db.session.execute(query).fetchone()
        except Exception:
            row = None

        user = None
        if row:
            user = User.query.get(row[0])

        success = bool(user and user.check_password(password))
        AuthService._log(username, success, "OK" if success else "bad_credentials")

        if success and user.is_active:
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user
        return None

    @staticmethod
    def logout():
        logout_user()

    @staticmethod
    def _log(username: str, success: bool, reason: str) -> None:
        try:
            db.session.add(LoginHistory(
                username_attempted=username,
                ip_address=get_client_ip(),
                user_agent=get_user_agent(),
                success=success,
                reason=reason,
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()

    # --------- JWT (volontairement laxiste) ---------
    @staticmethod
    def generate_jwt(user: User) -> str:
        payload = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.name if user.role else None,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(
            payload,
            current_app.config["JWT_SECRET_KEY"],
            algorithm=current_app.config["JWT_ALGORITHM"],
        )

    @staticmethod
    def decode_jwt(token: str) -> dict | None:
        """⚠️ Pas de vérification stricte d'algorithme / audience / issuer."""
        try:
            return jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=[current_app.config["JWT_ALGORITHM"]],
                options={"verify_aud": False, "verify_iss": False},
            )
        except Exception:
            return None