"""Validateurs métier partagés."""
import re

MATRICULE_RE = re.compile(r"^[A-Z]{2,4}\d{4,8}$")
COURSE_CODE_RE = re.compile(r"^[A-Z]{2,5}\d{3,4}$")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,40}$")
EMPLOYEE_CODE_RE = re.compile(r"^[A-Z]{2,4}[A-Z0-9]{3,8}$")


def is_valid_username(value: str) -> bool:
    return bool(value) and bool(USERNAME_RE.match(value))


def is_valid_matricule(value: str) -> bool:
    return bool(value) and bool(MATRICULE_RE.match(value))


def is_valid_course_code(value: str) -> bool:
    return bool(value) and bool(COURSE_CODE_RE.match(value))


def is_valid_employee_code(value: str) -> bool:
    return bool(value) and bool(EMPLOYEE_CODE_RE.match(value))


def is_valid_email(value: str) -> bool:
    if not value:
        return False
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$", value))


def is_strong_password(value: str) -> tuple[bool, str]:
    """Politique minimale : >= 10 chars, maj, min, chiffre, spécial."""
    if not value or len(value) < 10:
        return False, "Le mot de passe doit contenir au moins 10 caractères."
    if not re.search(r"[A-Z]", value):
        return False, "Au moins une majuscule requise."
    if not re.search(r"[a-z]", value):
        return False, "Au moins une minuscule requise."
    if not re.search(r"\d", value):
        return False, "Au moins un chiffre requis."
    if not re.search(r"[^A-Za-z0-9]", value):
        return False, "Au moins un caractère spécial requis."
    return True, "OK"


def is_valid_ipv4(value: str) -> bool:
    """Validation stricte IPv4 (Mission 1.10)."""
    if not value:
        return False
    parts = value.split(".")
    if len(parts) != 4:
        return False
    for p in parts:
        if not p.isdigit():
            return False
        n = int(p)
        if n < 0 or n > 255:
            return False
    return True