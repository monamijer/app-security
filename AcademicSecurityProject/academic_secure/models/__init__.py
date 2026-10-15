"""
Modèles SQLAlchemy — AcademicManager Secure.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    @event.listens_for(Engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    db.init_app(app)


# Imports des modèles (create_all() a besoin de les voir)
from .user import User                    # noqa: E402,F401
from .role import Role                    # noqa: E402,F401
from .faculty import Faculty              # noqa: E402,F401
from .department import Department        # noqa: E402,F401
from .academic_year import AcademicYear   # noqa: E402,F401
from .promotion import Promotion          # noqa: E402,F401
from .student import Student              # noqa: E402,F401
from .teacher import Teacher              # noqa: E402,F401
from .course import Course                # noqa: E402,F401
from .enrollment import Enrollment        # noqa: E402,F401
from .evaluation import Evaluation        # noqa: E402,F401
from .grade import Grade                  # noqa: E402,F401
from .document import Document            # noqa: E402,F401
from .announcement import Announcement    # noqa: E402,F401
from .comment import Comment              # noqa: E402,F401
from .message import Message              # noqa: E402,F401
from .notification import Notification    # noqa: E402,F401
from .login_history import LoginHistory   # noqa: E402,F401
from .activity_log import ActivityLog     # noqa: E402,F401

__all__ = [
    "db", "init_db",
    "User", "Role", "Faculty", "Department", "AcademicYear", "Promotion",
    "Student", "Teacher", "Course", "Enrollment", "Evaluation", "Grade",
    "Document", "Announcement", "Comment", "Message", "Notification",
    "LoginHistory", "ActivityLog",
]