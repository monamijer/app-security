from datetime import datetime, date
from . import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        unique=True, nullable=False)

    matricule = db.Column(db.String(30), unique=True, nullable=False, index=True)
    birth_date = db.Column(db.Date)
    birth_place = db.Column(db.String(150))
    gender = db.Column(db.String(10))
    nationality = db.Column(db.String(80), default="Burundaise")
    address = db.Column(db.String(255))
    photo_path = db.Column(db.String(255))
    enrollment_date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(30), default="active")

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"),
                              nullable=False)
    promotion_id = db.Column(db.Integer, db.ForeignKey("promotions.id"),
                             nullable=False)

    user = db.relationship("User", back_populates="student")
    department = db.relationship("Department", back_populates="students")
    promotion = db.relationship("Promotion", back_populates="students")

    enrollments = db.relationship("Enrollment", back_populates="student",
                                  cascade="all, delete-orphan", lazy="dynamic")
    grades = db.relationship("Grade", back_populates="student",
                             cascade="all, delete-orphan", lazy="dynamic")

    @property
    def full_name(self) -> str:
        return self.user.full_name if self.user else ""

    def __repr__(self) -> str:
        return f"<Student {self.matricule}>"