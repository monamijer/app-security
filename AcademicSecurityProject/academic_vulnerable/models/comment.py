from datetime import datetime
from . import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)   # ⚠️ brut
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    announcement_id = db.Column(db.Integer,
                                db.ForeignKey("announcements.id"),
                                nullable=False)

    author = db.relationship("User")
    announcement = db.relationship("Announcement", back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment {self.id} by user={self.author_id}>"