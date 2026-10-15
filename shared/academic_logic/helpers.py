"""Utilitaires partagés."""
from datetime import datetime
from flask import request


def get_client_ip() -> str:
    """Récupère l'IP cliente (derrière proxy éventuel)."""
    if request is None:
        return "0.0.0.0"
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.remote_addr or "0.0.0.0"


def get_user_agent() -> str:
    if request is None:
        return ""
    return (request.headers.get("User-Agent") or "")[:255]


def compute_average(grades: list[float]) -> float:
    if not grades:
        return 0.0
    return round(sum(grades) / len(grades), 2)


def compute_weighted_average(pairs: list[tuple[float, float]]) -> float:
    """pairs = [(score, weight), ...]"""
    if not pairs:
        return 0.0
    total_w = sum(w for _, w in pairs)
    if total_w == 0:
        return 0.0
    return round(sum(s * w for s, w in pairs) / total_w, 2)


def generate_matricule(prefix: str, number: int) -> str:
    return f"{prefix}{number:05d}"


def now_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")