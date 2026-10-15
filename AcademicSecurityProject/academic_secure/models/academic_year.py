from datetime import datetime, date
from . import db


class AcademicYear(db.Model):
    __tablename__ = "academic_years"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(20), unique=True, nullable=False)  # ex: "2025-2026"
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=False, default=date.today)
    is_current = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    promotions = db.relationship("Promotion", back_populates="academic_year",
                                 cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<AcademicYear {self.label}>"