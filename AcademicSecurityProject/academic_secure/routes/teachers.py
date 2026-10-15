from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from models import db
from models.teacher import Teacher
from models.department import Department
from models.user import User
from models.role import Role
from shared.academic_logic.validators import (
    is_valid_username, is_valid_email, is_valid_employee_code,
    is_strong_password,
)

teachers_bp = Blueprint("teachers", __name__)


@teachers_bp.route("/")
@login_required
def index():
    if current_user.has_role("student"):
        abort(403)
    q = (request.args.get("q") or "").strip()
    query = Teacher.query
    if q:
        like = f"%{q}%"
        query = query.filter(Teacher.employee_code.ilike(like))
    teachers = query.all()
    return render_template("teachers/list.html", teachers=teachers, q=q)


@teachers_bp.route("/<int:teacher_id>")
@login_required
def detail(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    return render_template("teachers/detail.html", teacher=teacher)


@teachers_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if not current_user.has_role("admin", "academic_manager"):
        abort(403)
    departments = Department.query.all()

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        first = (request.form.get("first_name") or "").strip()
        last = (request.form.get("last_name") or "").strip()
        employee_code = (request.form.get("employee_code") or "").strip().upper()
        try:
            dept_id = int(request.form.get("department_id", "0"))
        except ValueError:
            flash("Département invalide.", "danger")
            return redirect(url_for("teachers.create"))
        password = request.form.get("password") or ""

        if not is_valid_username(username):
            flash("Nom d'utilisateur invalide.", "danger")
            return redirect(url_for("teachers.create"))
        if not is_valid_email(email):
            flash("Email invalide.", "danger")
            return redirect(url_for("teachers.create"))
        if not is_valid_employee_code(employee_code):
            flash("Code employé invalide.", "danger")
            return redirect(url_for("teachers.create"))
        ok, msg = is_strong_password(password)
        if not ok:
            flash(msg, "danger")
            return redirect(url_for("teachers.create"))

        if User.query.filter_by(username=username).first():
            flash("Nom d'utilisateur déjà pris.", "danger")
            return redirect(url_for("teachers.create"))
        if Teacher.query.filter_by(employee_code=employee_code).first():
            flash("Code employé déjà utilisé.", "danger")
            return redirect(url_for("teachers.create"))

        role = Role.query.filter_by(name="teacher").first()
        u = User(username=username, email=email,
                 first_name=first[:80], last_name=last[:80], role=role)
        u.set_password(password)
        db.session.add(u)
        db.session.flush()

        t = Teacher(user_id=u.id, employee_code=employee_code,
                    department_id=dept_id)
        db.session.add(t)
        db.session.commit()
        flash("Enseignant créé.", "success")
        return redirect(url_for("teachers.index"))

    return render_template("teachers/form.html",
                           departments=departments, teacher=None)