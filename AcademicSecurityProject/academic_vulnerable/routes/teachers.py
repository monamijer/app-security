import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from models import db
from models.teacher import Teacher
from models.department import Department
from models.user import User
from models.role import Role

teachers_bp = Blueprint("teachers", __name__)


@teachers_bp.route("/")
@login_required
def index():
    if current_user.has_role("student"):
        abort(403)
    q = request.args.get("q", "")
    query = Teacher.query
    if q:
        from sqlalchemy import text
        rows = db.session.execute(
            text(f"SELECT id FROM teachers WHERE employee_code LIKE '%{q}%'")
        ).fetchall()
        ids = [r[0] for r in rows]
        query = query.filter(Teacher.id.in_(ids)) if ids else query.filter(False)
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
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        first = request.form.get("first_name", "").strip()
        last = request.form.get("last_name", "").strip()
        employee_code = request.form.get("employee_code", "").strip()
        dept_id = int(request.form.get("department_id", 0))
        password = request.form.get("password", "Teacher@2025!")

        role = Role.query.filter_by(name="teacher").first()
        u = User(username=username, email=email, first_name=first,
                 last_name=last, role=role)
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