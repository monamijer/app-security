"""
Utilitaires partagés pour AcademicSecurityProject.
Fournit les fonctions d'accès à la requête Flask utilisées par les services.
"""

from flask import request


def get_client_ip() -> str:
    """
    Retourne l'adresse IP du client.
    Gère le cas où l'application est derrière un proxy (X-Forwarded-For).
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For peut contenir plusieurs IP séparées par des virgules,
        # la première correspond au client d'origine.
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def get_user_agent() -> str:
    """
    Retourne le User-Agent du client, ou 'unknown' s'il est absent.
    """
    return request.headers.get("User-Agent", "unknown")


def get_request_headers() -> dict:
    """
    Retourne les en-têtes HTTP de la requête sous forme de dictionnaire.
    Utile pour les rapports du tableau de bord.
    """
    return dict(request.headers)


def is_https() -> bool:
    """
    Indique si la requête courante est en HTTPS.
    Prend en compte X-Forwarded-Proto (utile derrière Nginx).
    """
    if request.headers.get("X-Forwarded-Proto", "").lower() == "https":
        return True
    return request.is_secure


def anonymize_ip(ip: str) -> str:
    """
    Anonymise une adresse IP pour les rapports.
    - IPv4 : remplace le dernier octet par 'xxx'
    - IPv6 : remplace les 4 derniers groupes par 'xxxx'
    """
    if not ip or ip == "unknown":
        return "unknown"
    if ":" in ip:  # IPv6
        parts = ip.split(":")
        return ":".join(parts[:4] + ["xxxx", "xxxx", "xxxx", "xxxx"])
    parts = ip.split(".")
    if len(parts) == 4:
        return ".".join(parts[:3] + ["xxx"])
    return ip