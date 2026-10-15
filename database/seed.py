"""
Seed script — remplit les deux bases SQLite avec des données fictives
strictement identiques (sauf mécanisme de hash).

Usage (depuis la racine du projet) :
    python database/seed.py vulnerable
    python database/seed.py secure
    python database/seed.py both
"""
import os
import sys
import random
from datetime import date, datetime, timedelta

# Assure l'import depuis la bonne app
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _seed_app(app_name: str) -> None:
    app_dir = os.path.join(ROOT, f"academic_{app_name}")
    sys.path.insert(0, app_dir)

    # Purge des modules pour éviter les collisions entre les deux apps
    for mod in list(sys.modules.keys()):
        if mod.startswith(("models", "routes", "services", "config", "shared")):
            del sys.modules[mod]

    from app import create_app
    from models import db
    from models.user import User
    from models.role import Role
    from models.faculty import Faculty
    from models.department import Department
    from models.academic_year import AcademicYear
    from models.promotion import Promotion
    from models.student import Student
    from models.teacher import Teacher
    from models.course import Course
    from models.enrollment import Enrollment
    from models.evaluation import Evaluation
    from models.grade import Grade
    from models.announcement import Announcement
    from models.comment import Comment
    from models.notification import Notification
    from models.document import Document

    app = create_app()

    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- Rôles ---
        roles = {}
        for name, desc in [
            (Role.ADMIN, "Administrateur système"),
            (Role.ACADEMIC_MANAGER, "Responsable académique"),
            (Role.TEACHER, "Enseignant"),
            (Role.STUDENT, "Étudiant"),
        ]:
            r = Role(name=name, description=desc)
            db.session.add(r)
            roles[name] = r
        db.session.commit()

        # --- Facultés / Départements ---
        fac_sci = Faculty(name="Faculté des Sciences", code="FS",
                          description="Sciences exactes et naturelles",
                          dean_name="Dr. Ndayishimiye Pierre")
        fac_let = Faculty(name="Faculté des Lettres", code="FL",
                          description="Lettres et sciences humaines",
                          dean_name="Dr. Niyongabo Marie")
        db.session.add_all([fac_sci, fac_let])
        db.session.commit()

        dep_info = Department(name="Informatique", code="INFO",
                              head_name="Dr. Hakizimana Jean",
                              faculty=fac_sci)
        dep_math = Department(name="Mathématiques", code="MATH",
                              head_name="Dr. Nzeyimana Paul",
                              faculty=fac_sci)
        dep_lettres = Department(name="Lettres Modernes", code="LM",
                                 head_name="Dr. Uwimana Claire",
                                 faculty=fac_let)
        db.session.add_all([dep_info, dep_math, dep_lettres])
        db.session.commit()

        # --- Année académique ---
        ay = AcademicYear(label="2025-2026",
                          start_date=date(2025, 9, 1),
                          end_date=date(2026, 7, 15),
                          is_current=True)
        db.session.add(ay)
        db.session.commit()

        # --- Promotions ---
        prom_l3_info = Promotion(name="L3 Informatique", level="L3",
                                 academic_year=ay, department=dep_info)
        prom_l2_info = Promotion(name="L2 Informatique", level="L2",
                                 academic_year=ay, department=dep_info)
        prom_l3_math = Promotion(name="L3 Mathématiques", level="L3",
                                 academic_year=ay, department=dep_math)
        db.session.add_all([prom_l3_info, prom_l2_info, prom_l3_math])
        db.session.commit()

        # --- Utilisateurs ---
        def add_user(username, email, first, last, role_name, pwd):
            u = User(username=username, email=email,
                     first_name=first, last_name=last,
                     role=roles[role_name])
            u.set_password(pwd)
            db.session.add(u)
            return u

        admin = add_user("admin", "admin@univ.local",
                         "Alice", "Admin", Role.ADMIN, "Admin@2025!")
        rm1 = add_user("resp1", "resp1@univ.local",
                       "Bob", "Resp", Role.ACADEMIC_MANAGER, "Resp@2025!")
        rm2 = add_user("resp2", "resp2@univ.local",
                       "Chantal", "Resp", Role.ACADEMIC_MANAGER, "Resp@2025!")

        teachers_users = []
        for i, (first, last) in enumerate([
            ("David", "Nkurunziza"), ("Esther", "Iradukunda"),
            ("Fabrice", "Ndayizeye"), ("Grace", "Uwase"),
            ("Henri", "Bizimana"),
        ], start=1):
            u = add_user(f"teacher{i}", f"teacher{i}@univ.local",
                         first, last, Role.TEACHER, f"Teacher@2025!{i}")
            teachers_users.append(u)

        students_users = []
        first_names = ["Aline", "Bernard", "Cédric", "Diane", "Éric",
                       "Fiona", "Gabriel", "Hélène", "Isaac", "Josiane",
                       "Kevin", "Léa", "Marcel", "Nadia", "Olivier",
                       "Pauline", "Quentin", "Rachel", "Samuel", "Thérèse"]
        last_names = ["Niyonzima", "Hakizimana", "Ndayishimiye", "Uwimana",
                      "Nkurunziza", "Iradukunda", "Ndayizeye", "Uwase",
                      "Bizimana", "Ntibantunganya", "Nahimana", "Nkeshimana",
                      "Barankitse", "Nduwimana", "Nshimirimana", "Nsengiyumva",
                      "Mukamana", "Hategekimana", "Niyongabo", "Ntahompagaze"]
        for i in range(1, 21):
            fn = first_names[i - 1]
            ln = last_names[i - 1]
            u = add_user(f"student{i}", f"student{i}@univ.local",
                         fn, ln, Role.STUDENT, f"Student@2025!{i}")
            students_users.append(u)
        db.session.commit()

        # --- Profils enseignants ---
        teachers = []
        for i, u in enumerate(teachers_users, start=1):
            t = Teacher(user=u, employee_code=f"TCH{i:04d}",
                        grade="Maître-Assistant", specialty="Informatique",
                        department=dep_info, office=f"B{i:02d}")
            db.session.add(t)
            teachers.append(t)
        db.session.commit()

        # --- Profils étudiants ---
        students = []
        for i, u in enumerate(students_users, start=1):
            dep = dep_info if i <= 14 else (dep_math if i <= 18 else dep_lettres)
            prom = prom_l3_info if i <= 10 else (prom_l2_info if i <= 14
                                                 else prom_l3_math)
            s = Student(user=u, matricule=f"ETU{i:05d}",
                        birth_date=date(2000 + (i % 5), (i % 12) + 1, (i % 27) + 1),
                        gender="M" if i % 2 else "F",
                        department=dep, promotion=prom)
            db.session.add(s)
            students.append(s)
        db.session.commit()

        # --- Cours ---
        courses = []
        course_defs = [
            ("INFO301", "Bases de données avancées", 5, "S5", dep_info, teachers[0]),
            ("INFO302", "Sécurité applicative", 4, "S5", dep_info, teachers[1]),
            ("INFO303", "Développement Web", 4, "S5", dep_info, teachers[2]),
            ("INFO304", "Réseaux informatiques", 3, "S5", dep_info, teachers[3]),
            ("INFO305", "Génie logiciel", 3, "S6", dep_info, teachers[4]),
            ("MATH301", "Analyse numérique", 4, "S5", dep_math, teachers[0]),
            ("MATH302", "Algèbre linéaire", 3, "S5", dep_math, teachers[1]),
        ]
        for code, title, cred, sem, dep, t in course_defs:
            c = Course(code=code, title=title, credits=cred, semester=sem,
                       department=dep, teacher=t)
            db.session.add(c)
            courses.append(c)
        db.session.commit()

        # --- Inscriptions ---
        for s in students[:14]:
            for c in courses[:5]:
                db.session.add(Enrollment(student=s, course=c))
        db.session.commit()

        # --- Évaluations + Notes ---
        for c in courses[:5]:
            for ev_type, max_score, weight in [("controle", 20.0, 1.0),
                                               ("examen", 20.0, 2.0)]:
                ev = Evaluation(title=f"{ev_type.capitalize()} {c.code}",
                                type=ev_type, max_score=max_score,
                                weight=weight, course=c,
                                is_published=True)
                db.session.add(ev)
        db.session.commit()

        for ev in Evaluation.query.all():
            for enr in Enrollment.query.filter_by(course_id=ev.course_id).all():
                score = round(random.uniform(6.0, 19.0), 2)
                db.session.add(Grade(student_id=enr.student_id,
                                     evaluation_id=ev.id, score=score,
                                     entered_by_id=teachers[0].user_id))
        db.session.commit()

        # --- Annonces / Commentaires ---
        ann1 = Announcement(title="Bienvenue 2025-2026",
                            content="La rentrée académique est fixée au 1er septembre 2025.",
                            author=admin)
        ann2 = Announcement(title="Nouveaux supports disponibles",
                            content="Les supports du cours INFO302 sont en ligne.",
                            author=rm1, target_role=Role.STUDENT)
        db.session.add_all([ann1, ann2])
        db.session.commit()

        db.session.add_all([
            Comment(content="Merci pour l'information.", author=students_users[0],
                    announcement=ann1),
            Comment(content="Très utile.", author=students_users[1],
                    announcement=ann2),
        ])
        db.session.commit()

        # --- Notifications ---
        for u in students_users[:3]:
            db.session.add(Notification(title="Bienvenue",
                                        message="Votre compte a été créé.",
                                        user=u, category="info"))
        db.session.commit()

        print(f"✅ Seed terminé pour academic_{app_name} "
              f"({len(students_users)} étudiants, {len(teachers_users)} enseignants)")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "both"
    if target in ("vulnerable", "both"):
        _seed_app("vulnerable")
    if target in ("secure", "both"):
        _seed_app("secure")