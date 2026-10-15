from datetime import datetime
from . import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # 🔐 Nom original conservé à part, nom de stockage = UUID (jamais exposé)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), unique=True, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    sha256 = db.Column(db.String(64))         # intégrité
    is_public = db.Column(db.Boolean, default=False, nullable=False)

    owner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))

    owner = db.relationship("User")
    course = db.relationship("Course")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Document {self.title} ({self.stored_filename})>"