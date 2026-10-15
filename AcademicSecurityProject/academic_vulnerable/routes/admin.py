import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from functools import wraps

from models import db
from models.user import User
from models.role import Role
from models.faculty import Faculty
from models.department import Department
from models.academic_year import AcademicYear
from models.promotion import Promotion
from models.activity_log import ActivityLog
from models.login_history import LoginHistory

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.role:
            abort(403)
        if current_user.role.name not in ("admin", "academic_manager"):
            abort(403)
        return f(*args, **kwargs)
    return wrapper


@admin_bp.route("/users")
@admin_required
def users():
    q = request.args.get("q", "")
    if q:
        from sqlalchemy import text
        rows = db.session.execute(
            text(f"SELECT * FROM users WHERE username LIKE '%{q}%' "
                 f"OR email LIKE '%{q}%'")
        ).fetchall()
        ids = [r[0] for r in rows]
        users_list = User.query.filter(User.id.in_(ids)).all() if ids else []
    else:
        users_list = User.query.order_by(User.id).all()
    return render_template("admin/users.html", users=users_list, q=q)


@admin_bp.route("/users/create", methods=["POST"])
@admin_required
def create_user():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    first = request.form.get("first_name", "").strip()
    last = request.form.get("last_name", "").strip()
    role_name = request.form.get("role", "student")
    password = request.form.get("password", "Password@2025!")

    if User.query.filter_by(username=username).first():
        flash("Ce nom d'utilisateur existe déjà.", "danger")
        return redirect(url_for("admin.users"))

    role = Role.query.filter_by(name=role_name).first()
    if not role:
        flash("Rôle invalide.", "danger")
        return redirect(url_for("admin.users"))

    u = User(username=username, email=email, first_name=first,
             last_name=last, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    flash("Utilisateur créé.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@admin_required
def toggle_user(user_id):
    u = User.query.get_or_404(user_id)
    u.is_active = not u.is_active
    db.session.commit()
    flash("Statut modifié.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/faculties")
@admin_required
def faculties():
    items = Faculty.query.all()
    return render_template("admin/faculties.html", faculties=items)


@admin_bp.route("/faculties/create", methods=["POST"])
@admin_required
def create_faculty():
    f = Faculty(name=request.form.get("name", "").strip(),
                code=request.form.get("code", "").strip(),
                description=request.form.get("description", ""),
                dean_name=request.form.get("dean_name", ""))
    db.session.add(f)
    db.session.commit()
    flash("Faculté créée.", "success")
    return redirect(url_for("admin.faculties"))


@admin_bp.route("/departments")
@admin_required
def departments():
    items = Department.query.all()
    facs = Faculty.query.all()
    return render_template("admin/departments.html",
                           departments=items, faculties=facs)


@admin_bp.route("/departments/create", methods=["POST"])
@admin_required
def create_department():
    fac = Faculty.query.get(int(request.form.get("faculty_id")))
    if not fac:
        flash("Faculté invalide.", "danger")
        return redirect(url_for("admin.departments"))
    d = Department(name=request.form.get("name", "").strip(),
                   code=request.form.get("code", "").strip(),
                   head_name=request.form.get("head_name", ""),
                   faculty=fac)
    db.session.add(d)
    db.session.commit()
    flash("Département créé.", "success")
    return redirect(url_for("admin.departments"))


@admin_bp.route("/academic-years")
@admin_required
def academic_years():
    items = AcademicYear.query.order_by(AcademicYear.label.desc()).all()
    return render_template("admin/academic_years.html", years=items)


@admin_bp.route("/promotions")
@admin_required
def promotions():
    items = Promotion.query.all()
    return render_template("admin/promotions.html", promotions=items)


@admin_bp.route("/activity-logs")
@admin_required
def activity_logs():
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(200).all()
    return render_template("admin/activity_logs.html", logs=logs)


@admin_bp.route("/login-history")
@admin_required
def login_history():
    items = LoginHistory.query.order_by(LoginHistory.created_at.desc()).limit(200).all()
    return render_template("admin/activity_logs.html",
                           logs=items, title="Historique des connexions")


@admin_bp.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    if request.method == "POST":
        flash("Paramètres enregistrés (démo).", "success")
    return render_template("admin/settings.html")