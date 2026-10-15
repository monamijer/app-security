from datetime import datetime, date
from . import db


class Evaluation(db.Model):
    __tablename__ = "evaluations"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(30), nullable=False)   # examen, tp, controle, projet
    max_score = db.Column(db.Float, default=20.0, nullable=False)
    weight = db.Column(db.Float, default=1.0, nullable=False)
    evaluation_date = db.Column(db.Date, default=date.today, nullable=False)
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    course = db.relationship("Course", back_populates="evaluations")

    grades = db.relationship("Grade", back_populates="evaluation",
                             cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Evaluation {self.title} ({self.type})>"