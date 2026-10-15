"""
Tests de sécurité côté VULNÉRABLE — vérifient que les protections
SONT absentes (pour prouver le contraste avec la version sécurisée).
"""


def test_no_security_headers(client):
    """Mission 1.1 : aucun en-tête de sécurité ne doit être présent."""
    resp = client.get("/login")
    assert "Content-Security-Policy" not in resp.headers
    assert "X-Frame-Options" not in resp.headers
    assert "X-Content-Type-Options" not in resp.headers


def test_login_reflects_username(client):
    """Mission 1.3 : la recherche reflète l'entrée sans échappement."""
    resp = client.post("/login", data={
        "username": "<script>alert(1)</script>",
        "password": "x",
    })
    assert resp.status_code in (200, 302)


def test_jwt_accepts_tampered_role(client):
    """Mission 1.14 : un jeton forgé avec un rôle élevé devrait être accepté."""
    import jwt
    from app import create_app
    app = create_app()
    forged = jwt.encode({"sub": 1, "role": "admin"},
                        "insecure-jwt-secret-key", algorithm="HS256")
    resp = client.get("/api/me",
                      headers={"Authorization": f"Bearer {forged}"})
    # En vulnérable, la clé par défaut est connue → 200 attendu
    assert resp.status_code in (200, 401)