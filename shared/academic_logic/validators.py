import re
from email_validator import validate_email, EmailNotValidError


def is_valid_username(username):
    if not isinstance(username, str):
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,30}", username))


def is_valid_email(email):
    if not isinstance(email, str):
        return False
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def is_strong_password(password):
    if not isinstance(password, str):
        return False, "Mot de passe invalide."

    if len(password) < 12:
        return False, "Le mot de passe doit contenir au moins 12 caractères."

    if not re.search(r"[A-Z]", password):
        return False, "Ajoutez une lettre majuscule."

    if not re.search(r"[a-z]", password):
        return False, "Ajoutez une lettre minuscule."

    if not re.search(r"[0-9]", password):
        return False, "Ajoutez un chiffre."

    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Ajoutez un caractère spécial."

    return True, "Mot de passe valide."


def is_valid_matricule(matricule):
    if not isinstance(matricule, str):
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9/-]{3,30}", matricule))


def is_valid_employee_code(code):
    if not isinstance(code, str):
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{3,30}", code))


def is_valid_course_code(code):
    if not isinstance(code, str):
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{2,30}", code))