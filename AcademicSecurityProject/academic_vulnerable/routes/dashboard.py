import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from models import db
from models.student import Student
from models.teacher import Teacher
from models.course import Course
from models.grade import Grade
from models.department import Department

dashboard_bp = Blueprint("dashboard", __name__)


def _stats_for_admin():
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_courses = Course.query.count()
    avg_grade = db.session.query(func.avg(Grade.score)).scalar() or 0.0

    by_dept = (
        db.session.query(Department.name, func.count(Student.id))
        .join(Student, Student.department_id == Department.id)
        .group_by(Department.name)
        .all()
    )
    return {
        "students": total_students,
        "teachers": total_teachers,
        "courses": total_courses,
        "avg_grade": round(avg_grade, 2),
        "by_dept": [{"label": n, "value": c} for n, c in by_dept],
    }


@dashboard_bp.route("/dashboard")
@login_required
def index():
    role = current_user.role.name if current_user.role else None

    if role == "student":
        student = current_user.student
        grades = student.grades.all() if student else []
        avg = (sum(g.score for g in grades) / len(grades)) if grades else 0.0
        return render_template("students/dashboard.html",
                               student=student, avg=round(avg, 2),
                               grades=grades)

    if role == "teacher":
        teacher = current_user.teacher
        courses = teacher.courses.all() if teacher else []
        return render_template("teachers/dashboard.html",
                               teacher=teacher, courses=courses)

    return render_template("admin/dashboard.html", stats=_stats_for_admin())