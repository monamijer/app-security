"""
Constantes métier partagées entre les deux applications.
"""

ROLE_ADMIN = "admin"
ROLE_ACADEMIC_MANAGER = "academic_manager"
ROLE_TEACHER = "teacher"
ROLE_STUDENT = "student"

ALL_ROLES = [ROLE_ADMIN, ROLE_ACADEMIC_MANAGER, ROLE_TEACHER, ROLE_STUDENT]

ROLE_LABELS = {
    ROLE_ADMIN: "Administrateur",
    ROLE_ACADEMIC_MANAGER: "Responsable académique",
    ROLE_TEACHER: "Enseignant",
    ROLE_STUDENT: "Étudiant",
}

SEMESTERS = ["S1", "S2", "S3", "S4", "S5", "S6"]
LEVELS = ["L1", "L2", "L3", "M1", "M2"]
EVALUATION_TYPES = ["examen", "tp", "controle", "projet", "oral"]

STUDENT_STATUS = ["active", "suspended", "graduated"]
TEACHER_STATUS = ["active", "on_leave", "retired"]

GENDERS = ["M", "F"]

PER_PAGE_DEFAULT = 10

# Notifications
NOTIF_INFO = "info"
NOTIF_SUCCESS = "success"
NOTIF_WARNING = "warning"
NOTIF_DANGER = "danger"

GRADE_PASS_THRESHOLD = 10.0
GRADE_MAX = 20.0