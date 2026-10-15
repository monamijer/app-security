from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


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
        # ⚠️ VULNÉRABLE : hash faible (pbkdf2 sha256 avec 1 itération)
        # Mission 1.13 : cassable par Hashcat en quelques secondes.
        self.password_hash = generate_password_hash(
            password,
            method="pbkdf2:sha256:1",
            salt_length=4,
        )

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def has_role(self, *names: str) -> bool:
        return self.role is not None and self.role.name in names

    def __repr__(self) -> str:
        return f"<User {self.username}>"