from datetime import datetime
from . import db


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    users = db.relationship("User", back_populates="role", lazy="dynamic")

    # Constantes pratiques
    ADMIN = "admin"
    ACADEMIC_MANAGER = "academic_manager"
    TEACHER = "teacher"
    STUDENT = "student"

    @staticmethod
    def all_names() -> list[str]:
        return [Role.ADMIN, Role.ACADEMIC_MANAGER, Role.TEACHER, Role.STUDENT]

    def __repr__(self) -> str:
        return f"<Role {self.name}>"