import os
import sys

# Ajoute la racine du projet au PYTHONPATH pour importer shared/
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

"""
AcademicManager Secure — Application factory.
"""
from flask import Flask, render_template
from flask_login import LoginManager

from config import Config
from models import db, init_db
from models.user import User
# ... etc


login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Veuillez vous connecter."
login_manager.login_message_category = "warning"
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    init_db(app)
    login_manager.init_app(app)

    # CSRF global (Flask-WTF)
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.admin import admin_bp
    from routes.students import students_bp
    from routes.teachers import teachers_bp
    from routes.courses import courses_bp
    from routes.grades import grades_bp
    from routes.documents import documents_bp
    from routes.announcements import announcements_bp
    from routes.messages import messages_bp
    from routes.diagnostics import diagnostics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(teachers_bp, url_prefix="/teachers")
    app.register_blueprint(courses_bp, url_prefix="/courses")
    app.register_blueprint(grades_bp, url_prefix="/grades")
    app.register_blueprint(documents_bp, url_prefix="/documents")
    app.register_blueprint(announcements_bp, url_prefix="/announcements")
    app.register_blueprint(messages_bp, url_prefix="/messages")
    app.register_blueprint(diagnostics_bp, url_prefix="/admin/diagnostics")

    # 🔐 Headers de sécurité (Mission 1.1, 1.4, 1.5, 1.6, 1.7, 1.8)
    @app.after_request
    def _security_headers(response):
        for header, value in app.config.get("SECURITY_HEADERS", {}).items():
            response.headers.setdefault(header, value)
        # Supprime les headers qui fuitent la stack
        response.headers.pop("Server", None)
        response.headers.pop("X-Powered-By", None)
        return response

    @app.errorhandler(404)
    def _404(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def _500(e):
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def _403(e):
        return render_template("errors/403.html"), 403

    @app.route("/")
    def index():
        from flask import redirect, url_for
        return redirect(url_for("dashboard.index"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8081, debug=False)