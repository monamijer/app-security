from datetime import datetime
from . import db


class Grade(db.Model):
    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float, nullable=False, default=0.0)
    comment = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    evaluation_id = db.Column(db.Integer, db.ForeignKey("evaluations.id"),
                              nullable=False)
    entered_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    student = db.relationship("Student", back_populates="grades")
    evaluation = db.relationship("Evaluation", back_populates="grades")
    entered_by = db.relationship("User")

    __table_args__ = (
        db.UniqueConstraint("student_id", "evaluation_id",
                            name="uq_grade_student_evaluation"),
    )

    def __repr__(self) -> str:
        return f"<Grade s={self.student_id} e={self.evaluation_id} {self.score}>"