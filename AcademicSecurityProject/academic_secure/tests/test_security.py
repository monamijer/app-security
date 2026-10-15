"""
Tests de sécurité côté SÉCURISÉ — vérifient que les protections
SONT actives et bloquent les comportements non autorisés.
"""


def test_security_headers_present(client):
    """Mission 1.1 : les en-têtes doivent être présents."""
    resp = client.get("/login")
    assert "Content-Security-Policy" in resp.headers
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["X-Content-Type-Options"] == "nosniff"


def test_csp_is_restrictive(client):
    """Mission 1.3 : CSP ne doit pas contenir unsafe-inline pour script-src."""
    csp = client.get("/login").headers.get("Content-Security-Policy", "")
    assert "script-src 'self'" in csp
    assert "unsafe-inline" not in csp.split("script-src")[1].split(";")[0]


def test_jwt_rejects_tampered_signature(client):
    """Mission 1.14 : un jeton forgé doit être refusé."""
    import jwt
    forged = jwt.encode({"sub": "1", "role": "admin"},
                        "wrong-secret", algorithm="HS256")
    resp = client.get("/api/me",
                      headers={"Authorization": f"Bearer {forged}"})
    assert resp.status_code == 401


def test_jwt_rejects_alg_none(client):
    """Mission 1.14 : alg=none doit être refusé."""
    resp = client.get("/api/me",
                      headers={"Authorization": "Bearer eyJhbGciOiJub25lIn0.eyJzdWIiOiIxIn0."})
    assert resp.status_code == 401


def test_path_traversal_blocked(client):
    """Mission 1.12 : tentative de traversée de chemin bloquée."""
    resp = client.get("/documents/download/../../etc/passwd")
    assert resp.status_code in (400, 403, 404)


def test_csrf_token_required(client):
    """Mission 1.4 : requête POST sans jeton CSRF rejetée."""
    resp = client.post("/admin/faculties/create", data={"name": "X", "code": "X"})
    # Sans authentification → 302 vers login, avec auth → 400 CSRF
    assert resp.status_code in (302, 400)