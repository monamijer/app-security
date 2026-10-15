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
from shared.academic_logic.helpers import get_client_ip

admin_bp = Blueprint("admin", __name__)


# 🔐 Décorateur strict + journalisation
def admin_required(f):
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_active:
            abort(403)
        if not current_user.role or current_user.role.name not in ("admin",):
            # L'academic_manager a ses propres routes (à ajouter plus tard si besoin)
            if not current_user.has_role("admin", "academic_manager"):
                abort(403)
        return f(*args, **kwargs)
    return wrapper


def _log(action: str, entity: str = None, entity_id: int = None,
         details: str = None) -> None:
    db.session.add(ActivityLog(
        user_id=current_user.id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details,
        ip_address=get_client_ip(),
    ))
    db.session.commit()


@admin_bp.route("/users")
@admin_required
def users():
    q = (request.args.get("q") or "").strip()
    query = User.query
    if q:
        # 🔐 requêtes paramétrées via ORM (Mission 1.9)
        like = f"%{q}%"
        query = query.filter(db.or_(User.username.ilike(like),
                                    User.email.ilike(like)))
    users_list = query.order_by(User.id).all()
    return render_template("admin/users.html", users=users_list, q=q)


@admin_bp.route("/users/create", methods=["POST"])
@admin_required
def create_user():
    from shared.academic_logic.validators import (
        is_valid_username, is_valid_email, is_strong_password
    )

    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    first = (request.form.get("first_name") or "").strip()
    last = (request.form.get("last_name") or "").strip()
    role_name = request.form.get("role", "student")
    password = request.form.get("password") or ""

    if not is_valid_username(username):
        flash("Nom d'utilisateur invalide.", "danger")
        return redirect(url_for("admin.users"))
    if not is_valid_email(email):
        flash("Email invalide.", "danger")
        return redirect(url_for("admin.users"))
    ok, msg = is_strong_password(password)
    if not ok:
        flash(msg, "danger")
        return redirect(url_for("admin.users"))

    if User.query.filter_by(username=username).first():
        flash("Ce nom d'utilisateur existe déjà.", "danger")
        return redirect(url_for("admin.users"))

    role = Role.query.filter_by(name=role_name).first()
    if not role:
        flash("Rôle invalide.", "danger")
        return redirect(url_for("admin.users"))

    u = User(username=username, email=email,
             first_name=first[:80], last_name=last[:80], role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    _log("create_user", "user", u.id, f"role={role_name}")
    flash("Utilisateur créé.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@admin_required
def toggle_user(user_id):
    u = User.query.get_or_404(user_id)
    if u.id == current_user.id:
        flash("Impossible de désactiver votre propre compte.", "danger")
        return redirect(url_for("admin.users"))
    u.is_active = not u.is_active
    db.session.commit()
    _log("toggle_user", "user", u.id, f"active={u.is_active}")
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
    name = (request.form.get("name") or "").strip()
    code = (request.form.get("code") or "").strip().upper()
    if not name or not code or len(code) > 20:
        flash("Champs invalides.", "danger")
        return redirect(url_for("admin.faculties"))

    f = Faculty(name=name[:150], code=code,
                description=(request.form.get("description") or "")[:5000],
                dean_name=(request.form.get("dean_name") or "")[:150])
    db.session.add(f)
    db.session.commit()
    _log("create_faculty", "faculty", f.id)
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
    try:
        fid = int(request.form.get("faculty_id", "0"))
    except ValueError:
        fid = 0
    fac = Faculty.query.get(fid)
    if not fac:
        flash("Faculté invalide.", "danger")
        return redirect(url_for("admin.departments"))

    d = Department(name=(request.form.get("name") or "")[:150],
                   code=(request.form.get("code") or "").upper()[:20],
                   head_name=(request.form.get("head_name") or "")[:150],
                   faculty=fac)
    db.session.add(d)
    db.session.commit()
    _log("create_department", "department", d.id)
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
    logs = (ActivityLog.query
            .order_by(ActivityLog.created_at.desc())
            .limit(200).all())
    return render_template("admin/activity_logs.html", logs=logs)


@admin_bp.route("/login-history")
@admin_required
def login_history():
    items = (LoginHistory.query
             .order_by(LoginHistory.created_at.desc())
             .limit(200).all())
    return render_template("admin/activity_logs.html",
                           logs=items, title="Historique des connexions")


@admin_bp.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    if request.method == "POST":
        _log("update_settings", "settings")
        flash("Paramètres enregistrés.", "success")
    return render_template("admin/settings.html")