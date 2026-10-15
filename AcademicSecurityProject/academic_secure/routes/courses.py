from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from models import db
from models.course import Course
from models.department import Department
from models.teacher import Teacher
from models.enrollment import Enrollment
from shared.academic_logic.validators import is_valid_course_code

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/")
@login_required
def index():
    q = (request.args.get("q") or "").strip()
    query = Course.query
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Course.title.ilike(like),
                                    Course.code.ilike(like)))
    courses = query.all()
    # 🔐 q est échappé par Jinja dans le template (pas de |safe)
    return render_template("courses/list.html", courses=courses, q=q)


@courses_bp.route("/<int:course_id>")
@login_required
def detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template("courses/detail.html", course=course)


@courses_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if not current_user.has_role("admin", "academic_manager"):
        abort(403)
    departments = Department.query.all()
    teachers = Teacher.query.all()

    if request.method == "POST":
        code = (request.form.get("code") or "").strip().upper()
        title = (request.form.get("title") or "").strip()
        if not is_valid_course_code(code):
            flash("Code de cours invalide (ex: INFO301).", "danger")
            return redirect(url_for("courses.create"))
        try:
            credits = int(request.form.get("credits", "3"))
            dept_id = int(request.form.get("department_id", "0"))
        except ValueError:
            flash("Champs numériques invalides.", "danger")
            return redirect(url_for("courses.create"))

        teacher_id = request.form.get("teacher_id")
        teacher_id = int(teacher_id) if teacher_id else None

        c = Course(
            code=code, title=title[:200],
            description=(request.form.get("description") or "")[:5000],
            credits=max(1, min(credits, 12)),
            semester=request.form.get("semester", "S1"),
            department_id=dept_id,
            teacher_id=teacher_id,
        )
        db.session.add(c)
        db.session.commit()
        flash("Cours créé.", "success")
        return redirect(url_for("courses.index"))

    return render_template("courses/form.html",
                           departments=departments, teachers=teachers, course=None)


@courses_bp.route("/<int:course_id>/enroll", methods=["POST"])
@login_required
def enroll(course_id):
    if not current_user.has_role("student"):
        abort(403)
    course = Course.query.get_or_404(course_id)
    if not current_user.student:
        abort(403)

    # 🔐 limite de capacité contrôlée
    current_count = Enrollment.query.filter_by(course_id=course.id).count()
    if current_count >= (course.max_students or 60):
        flash("Cours complet.", "warning")
        return redirect(url_for("courses.detail", course_id=course.id))

    exists = Enrollment.query.filter_by(
        student_id=current_user.student.id, course_id=course.id
    ).first()
    if not exists:
        db.session.add(Enrollment(student_id=current_user.student.id,
                                  course_id=course.id))
        db.session.commit()
        flash("Inscription réussie.", "success")
    return redirect(url_for("courses.detail", course_id=course.id))