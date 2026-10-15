import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file
from flask_login import login_required, current_user
from io import BytesIO

from models import db
from models.grade import Grade
from models.evaluation import Evaluation
from models.course import Course
from models.student import Student

grades_bp = Blueprint("grades", __name__)


@grades_bp.route("/")
@login_required
def index():
    if current_user.has_role("student"):
        student = current_user.student
        grades = student.grades.all() if student else []
        return render_template("grades/list.html", grades=grades, student=student)
    grades = Grade.query.limit(200).all()
    return render_template("grades/list.html", grades=grades, student=None)


@grades_bp.route("/student/<int:student_id>")
@login_required
def by_student(student_id):
    student = Student.query.get_or_404(student_id)
    grades = student.grades.all()
    return render_template("grades/list.html", grades=grades, student=student)


@grades_bp.route("/evaluation/<int:evaluation_id>", methods=["GET", "POST"])
@login_required
def enter_grades(evaluation_id):
    if not current_user.has_role("teacher", "admin", "academic_manager"):
        abort(403)
    ev = Evaluation.query.get_or_404(evaluation_id)

    if request.method == "POST":
        for key, value in request.form.items():
            if key.startswith("score_"):
                sid = int(key.replace("score_", ""))
                try:
                    score = float(value)
                except ValueError:
                    continue
                g = Grade.query.filter_by(student_id=sid,
                                          evaluation_id=ev.id).first()
                if g:
                    g.score = score
                else:
                    db.session.add(Grade(student_id=sid, evaluation_id=ev.id,
                                         score=score,
                                         entered_by_id=current_user.id))
        db.session.commit()
        flash("Notes enregistrées.", "success")
        return redirect(url_for("grades.enter_grades", evaluation_id=ev.id))

    enrollments = ev.course.enrollments.all()
    students = [e.student for e in enrollments]
    existing = {g.student_id: g for g in ev.grades.all()}
    return render_template("grades/form.html",
                           evaluation=ev, students=students, existing=existing)


@grades_bp.route("/transcript/<int:student_id>.pdf")
@login_required
def transcript_pdf(student_id):
    student = Student.query.get_or_404(student_id)
    from reportlab.pdfgen import canvas
    buf = BytesIO()
    p = canvas.Canvas(buf)
    p.drawString(100, 800, f"Relevé de {student.full_name} ({student.matricule})")
    y = 770
    for g in student.grades.all():
        p.drawString(100, y, f"{g.evaluation.course.code} - {g.evaluation.title}: {g.score}")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
    p.save()
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf",
                     download_name=f"transcript_{student.matricule}.pdf")