import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.role import Role
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = AuthService.authenticate(username, password)
        if user:
            flash("Connexion réussie.", "success")
            return redirect(url_for("dashboard.index"))
        flash("Identifiants invalides.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    AuthService.logout()
    flash("Déconnexion effectuée.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile")
@login_required
def profile():
    return render_template("auth/profile.html", user=current_user)


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old = request.form.get("old_password", "")
        new = request.form.get("new_password", "")
        if not current_user.check_password(old):
            flash("Ancien mot de passe incorrect.", "danger")
        else:
            current_user.set_password(new)
            db.session.commit()
            flash("Mot de passe modifié.", "success")
            return redirect(url_for("auth.profile"))
    return render_template("auth/change_password.html")


@auth_bp.route("/api/token", methods=["POST"])
def api_token():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid_credentials"}), 401
    token = AuthService.generate_jwt(user)
    return jsonify({"token": token})


@auth_bp.route("/api/me", methods=["GET"])
def api_me():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "missing_token"}), 401
    payload = AuthService.decode_jwt(auth[7:])
    if not payload:
        return jsonify({"error": "invalid_token"}), 401
    return jsonify({"user_id": payload.get("sub"),
                    "role": payload.get("role")})