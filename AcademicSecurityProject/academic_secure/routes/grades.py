from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file
from flask_login import login_required, current_user
from io import BytesIO

from models import db
from models.grade import Grade
from models.evaluation import Evaluation
from models.course import Course
from models.student import Student
from shared.academic_logic.helpers import get_client_ip

grades_bp = Blueprint("grades", __name__)


def _can_view_student(student: Student) -> bool:
    if current_user.has_role("admin", "academic_manager"):
        return True
    if current_user.has_role("teacher"):
        teacher = current_user.teacher
        if not teacher:
            return False
        course_ids = {c.id for c in teacher.courses.all()}
        return any(e.course_id in course_ids for e in student.enrollments.all())
    if current_user.has_role("student"):
        return current_user.student and current_user.student.id == student.id
    return False


@grades_bp.route("/")
@login_required
def index():
    if current_user.has_role("student"):
        student = current_user.student
        grades = student.grades.all() if student else []
        return render_template("grades/list.html", grades=grades, student=student)

    if current_user.has_role("teacher"):
        teacher = current_user.teacher
        course_ids = [c.id for c in teacher.courses.all()] if teacher else []
        grades = (Grade.query
                  .join(Evaluation, Grade.evaluation_id == Evaluation.id)
                  .filter(Evaluation.course_id.in_(course_ids))
                  .limit(300).all()) if course_ids else []
        return render_template("grades/list.html", grades=grades, student=None)

    grades = Grade.query.limit(200).all()
    return render_template("grades/list.html", grades=grades, student=None)


@grades_bp.route("/student/<int:student_id>")
@login_required
def by_student(student_id):
    student = Student.query.get_or_404(student_id)
    if not _can_view_student(student):
        abort(403)  # 🔐 IDOR bloqué
    grades = student.grades.all()
    return render_template("grades/list.html", grades=grades, student=student)


@grades_bp.route("/evaluation/<int:evaluation_id>", methods=["GET", "POST"])
@login_required
def enter_grades(evaluation_id):
    if not current_user.has_role("teacher", "admin", "academic_manager"):
        abort(403)
    ev = Evaluation.query.get_or_404(evaluation_id)

    # 🔐 un teacher ne peut noter que ses cours
    if current_user.has_role("teacher"):
        teacher = current_user.teacher
        if not teacher or ev.course.teacher_id != teacher.id:
            abort(403)

    if request.method == "POST":
        for key, value in request.form.items():
            if not key.startswith("score_"):
                continue
            try:
                sid = int(key.replace("score_", ""))
                score = float(value)
            except (ValueError, TypeError):
                continue
            # 🔐 validation de la plage
            if score < 0 or score > (ev.max_score or 20.0):
                continue
            # 🔐 l'étudiant doit être inscrit à ce cours
            if not any(e.student_id == sid for e in ev.course.enrollments.all()):
                continue

            g = Grade.query.filter_by(student_id=sid, evaluation_id=ev.id).first()
            if g:
                g.score = score
                g.entered_by_id = current_user.id
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
    if not _can_view_student(student):
        abort(403)  # 🔐
    from reportlab.pdfgen import canvas
    buf = BytesIO()
    p = canvas.Canvas(buf)
    p.drawString(100, 800, f"Relevé de {student.full_name} ({student.matricule})")
    y = 770
    for g in student.grades.all():
        p.drawString(100, y,
                     f"{g.evaluation.course.code} - {g.evaluation.title}: {g.score}")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
    p.save()
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf",
                     download_name=f"transcript_{student.matricule}.pdf")