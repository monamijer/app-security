from datetime import datetime
from . import db


class Announcement(db.Model):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    # ⚠️ Contenu brut stocké, rendu avec |safe plus tard (Mission 1.11)
    content = db.Column(db.Text, nullable=False)
    target_role = db.Column(db.String(50))   # null = tous
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User")

    comments = db.relationship("Comment", back_populates="announcement",
                               cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Announcement {self.title}>"