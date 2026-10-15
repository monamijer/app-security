import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from models import db
from models.course import Course
from models.department import Department
from models.teacher import Teacher
from models.enrollment import Enrollment

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "")
    query = Course.query
    if q:
        from sqlalchemy import text
        rows = db.session.execute(
            text(f"SELECT id FROM courses WHERE title LIKE '%{q}%' "
                 f"OR code LIKE '%{q}%'")
        ).fetchall()
        ids = [r[0] for r in rows]
        query = query.filter(Course.id.in_(ids)) if ids else query.filter(False)
    courses = query.all()
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
        c = Course(
            code=request.form.get("code", "").strip(),
            title=request.form.get("title", "").strip(),
            description=request.form.get("description", ""),
            credits=int(request.form.get("credits", 3)),
            semester=request.form.get("semester", "S1"),
            department_id=int(request.form.get("department_id", 0)),
            teacher_id=(int(request.form.get("teacher_id"))
                        if request.form.get("teacher_id") else None),
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
    exists = Enrollment.query.filter_by(
        student_id=current_user.student.id, course_id=course.id
    ).first()
    if not exists:
        db.session.add(Enrollment(student_id=current_user.student.id,
                                  course_id=course.id))
        db.session.commit()
        flash("Inscription réussie.", "success")
    return redirect(url_for("courses.detail", course_id=course.id))