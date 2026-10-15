import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from models import db
from models.student import Student
from models.department import Department
from models.promotion import Promotion
from models.user import User
from models.role import Role

students_bp = Blueprint("students", __name__)


def _can_manage_students() -> bool:
    return current_user.has_role("admin", "academic_manager")


@students_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "")
    if _can_manage_students():
        query = Student.query
        if q:
            from sqlalchemy import text
            rows = db.session.execute(
                text(f"SELECT id FROM students WHERE matricule LIKE '%{q}%'")
            ).fetchall()
            ids = [r[0] for r in rows]
            query = query.filter(Student.id.in_(ids)) if ids else query.filter(False)
        students = query.order_by(Student.id).all()
    else:
        students = [current_user.student] if current_user.student else []
    return render_template("students/list.html", students=students, q=q)


@students_bp.route("/<int:student_id>")
@login_required
def detail(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template("students/detail.html", student=student)


@students_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if not _can_manage_students():
        abort(403)

    departments = Department.query.all()
    promotions = Promotion.query.all()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        first = request.form.get("first_name", "").strip()
        last = request.form.get("last_name", "").strip()
        matricule = request.form.get("matricule", "").strip()
        dept_id = int(request.form.get("department_id", 0))
        prom_id = int(request.form.get("promotion_id", 0))
        password = request.form.get("password", "Student@2025!")

        if User.query.filter_by(username=username).first():
            flash("Nom d'utilisateur déjà pris.", "danger")
            return redirect(url_for("students.create"))

        role = Role.query.filter_by(name="student").first()
        u = User(username=username, email=email, first_name=first,
                 last_name=last, role=role)
        u.set_password(password)
        db.session.add(u)
        db.session.flush()

        s = Student(user_id=u.id, matricule=matricule,
                    department_id=dept_id, promotion_id=prom_id)
        db.session.add(s)
        db.session.commit()
        flash("Étudiant créé.", "success")
        return redirect(url_for("students.index"))

    return render_template("students/form.html",
                           departments=departments, promotions=promotions,
                           student=None)