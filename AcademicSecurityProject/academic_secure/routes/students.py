from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from models import db
from models.student import Student
from models.department import Department
from models.promotion import Promotion
from models.user import User
from models.role import Role
from shared.academic_logic.validators import is_valid_username, is_valid_email, is_valid_matricule
from shared.academic_logic.helpers import get_client_ip

students_bp = Blueprint("students", __name__)


def _can_manage_students() -> bool:
    return current_user.has_role("admin", "academic_manager")


def _can_view(student: Student) -> bool:
    """🔐 Contrôle d'accès strict (anti-IDOR, Mission 1.3/1.11)."""
    if _can_manage_students():
        return True
    if current_user.has_role("teacher"):
        # Un enseignant voit les étudiants de ses cours
        teacher = current_user.teacher
        if not teacher:
            return False
        course_ids = [c.id for c in teacher.courses.all()]
        return any(e.course_id in course_ids for e in student.enrollments.all())
    if current_user.has_role("student"):
        return current_user.student and current_user.student.id == student.id
    return False


@students_bp.route("/")
@login_required
def index():
    q = (request.args.get("q") or "").strip()

    if _can_manage_students():
        query = Student.query
        if q:
            # 🔐 ORM paramétré
            like = f"%{q}%"
            query = query.filter(Student.matricule.ilike(like))
        students = query.order_by(Student.id).all()
    elif current_user.has_role("teacher"):
        teacher = current_user.teacher
        course_ids = [c.id for c in teacher.courses.all()] if teacher else []
        students = (
            Student.query
            .join(Student.enrollments)
            .filter_by(course_id=course_ids[0]) if course_ids else []
        )
        if not isinstance(students, list):
            students = list({s.id: s for s in students}.values())
        if q:
            like = f"%{q.lower()}%"
            students = [s for s in students if like in s.matricule.lower()]
    elif current_user.has_role("student"):
        students = [current_user.student] if current_user.student else []
    else:
        students = []

    return render_template("students/list.html", students=students, q=q)


@students_bp.route("/<int:student_id>")
@login_required
def detail(student_id):
    student = Student.query.get_or_404(student_id)
    if not _can_view(student):
        abort(403)  # 🔐 IDOR bloqué
    return render_template("students/detail.html", student=student)


@students_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if not _can_manage_students():
        abort(403)

    departments = Department.query.all()
    promotions = Promotion.query.all()

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        first = (request.form.get("first_name") or "").strip()
        last = (request.form.get("last_name") or "").strip()
        matricule = (request.form.get("matricule") or "").strip().upper()
        try:
            dept_id = int(request.form.get("department_id", "0"))
            prom_id = int(request.form.get("promotion_id", "0"))
        except ValueError:
            flash("Sélection invalide.", "danger")
            return redirect(url_for("students.create"))
        password = request.form.get("password") or ""

        from shared.academic_logic.validators import is_strong_password

        if not is_valid_username(username):
            flash("Nom d'utilisateur invalide.", "danger")
            return redirect(url_for("students.create"))
        if not is_valid_email(email):
            flash("Email invalide.", "danger")
            return redirect(url_for("students.create"))
        if not is_valid_matricule(matricule):
            flash("Matricule invalide (ex: ETU00001).", "danger")
            return redirect(url_for("students.create"))
        ok, msg = is_strong_password(password)
        if not ok:
            flash(msg, "danger")
            return redirect(url_for("students.create"))

        if User.query.filter_by(username=username).first():
            flash("Nom d'utilisateur déjà pris.", "danger")
            return redirect(url_for("students.create"))
        if Student.query.filter_by(matricule=matricule).first():
            flash("Matricule déjà utilisé.", "danger")
            return redirect(url_for("students.create"))

        role = Role.query.filter_by(name="student").first()
        u = User(username=username, email=email,
                 first_name=first[:80], last_name=last[:80], role=role)
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