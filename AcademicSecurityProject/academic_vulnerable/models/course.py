from datetime import datetime
from . import db


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, default=3, nullable=False)
    semester = db.Column(db.String(10), nullable=False)   # S1..S6
    hours = db.Column(db.Integer, default=30)
    max_students = db.Column(db.Integer, default=60)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"),
                              nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))

    department = db.relationship("Department", back_populates="courses")
    teacher = db.relationship("Teacher", back_populates="courses")

    enrollments = db.relationship("Enrollment", back_populates="course",
                                  cascade="all, delete-orphan", lazy="dynamic")
    evaluations = db.relationship("Evaluation", back_populates="course",
                                  cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Course {self.code}>"