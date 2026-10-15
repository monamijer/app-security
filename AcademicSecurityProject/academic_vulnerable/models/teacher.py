from datetime import date
from . import db


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        unique=True, nullable=False)

    employee_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    grade = db.Column(db.String(50))            # Assistant, Maître-Assistant, etc.
    specialty = db.Column(db.String(150))
    hire_date = db.Column(db.Date, default=date.today, nullable=False)
    office = db.Column(db.String(50))
    status = db.Column(db.String(30), default="active")

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"),
                              nullable=False)
    department = db.relationship("Department", back_populates="teachers")

    user = db.relationship("User", back_populates="teacher")
    courses = db.relationship("Course", back_populates="teacher", lazy="dynamic")

    @property
    def full_name(self) -> str:
        return self.user.full_name if self.user else ""

    def __repr__(self) -> str:
        return f"<Teacher {self.employee_code}>"