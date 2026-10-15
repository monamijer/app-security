from datetime import datetime
from . import db


class Promotion(db.Model):
    __tablename__ = "promotions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)   # ex: "L3 Informatique"
    level = db.Column(db.String(20), nullable=False)   # L1, L2, L3, M1, M2
    capacity = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    academic_year_id = db.Column(db.Integer,
                                 db.ForeignKey("academic_years.id"),
                                 nullable=False)
    academic_year = db.relationship("AcademicYear", back_populates="promotions")

    department_id = db.Column(db.Integer,
                              db.ForeignKey("departments.id"),
                              nullable=False)
    department = db.relationship("Department")

    students = db.relationship("Student", back_populates="promotion", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint("academic_year_id", "department_id", "level",
                            name="uq_promotion_year_dept_level"),
    )

    def __repr__(self) -> str:
        return f"<Promotion {self.name}>"