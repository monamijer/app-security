from datetime import datetime
from flask_login import UserMixin
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
from . import db

_ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(30))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    role = db.relationship("Role", back_populates="users", lazy="joined")

    student = db.relationship("Student", back_populates="user", uselist=False,
                              cascade="all, delete-orphan")
    teacher = db.relationship("Teacher", back_populates="user", uselist=False,
                              cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        """Argon2id avec sel unique (Mission 1.13)."""
        self.password_hash = _ph.hash(password)

    def check_password(self, password: str) -> bool:
        try:
            _ph.verify(self.password_hash, password)
            if _ph.check_needs_rehash(self.password_hash):
                self.password_hash = _ph.hash(password)
            return True
        except (VerifyMismatchError, VerificationError, InvalidHash):
            return False

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def has_role(self, *names: str) -> bool:
        return self.role is not None and self.role.name in names

    def __repr__(self) -> str:
        return f"<User {self.username}>"