from datetime import datetime
from . import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(20), nullable=False, index=True)
    description = db.Column(db.Text)
    head_name = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=False)
    faculty = db.relationship("Faculty", back_populates="departments")

    students = db.relationship("Student", back_populates="department", lazy="dynamic")
    teachers = db.relationship("Teacher", back_populates="department", lazy="dynamic")
    courses = db.relationship("Course", back_populates="department", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint("faculty_id", "code", name="uq_department_faculty_code"),
    )

    def __repr__(self) -> str:
        return f"<Department {self.code}>"