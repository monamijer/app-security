import os
import uuid
import hashlib
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, abort, send_file, current_app)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename, safe_join
from models import db
from models.document import Document

documents_bp = Blueprint("documents", __name__)


def _allowed(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def _check_magic(path: str) -> str | None:
    """🔐 Détection de signature basique (Mission 1.5)."""
    with open(path, "rb") as fh:
        head = fh.read(16)
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"%PDF-"):
        return "application/pdf"
    return None


@documents_bp.route("/")
@login_required
def index():
    if current_user.has_role("admin", "academic_manager"):
        docs = Document.query.all()
    else:
        docs = Document.query.filter(
            db.or_(Document.owner_user_id == current_user.id,
                   Document.is_public == True)  # noqa
        ).all()
    return render_template("documents/list.html", documents=docs)


@documents_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        f = request.files.get("file")
        title = (request.form.get("title") or "").strip()
        if not f or not f.filename:
            flash("Aucun fichier.", "danger")
            return redirect(url_for("documents.upload"))

        original = secure_filename(f.filename)
        if not _allowed(original):
            flash("Extension non autorisée.", "danger")
            return redirect(url_for("documents.upload"))

        # 🔐 nom aléatoire, jamais exposé
        ext = original.rsplit(".", 1)[1].lower()
        stored = f"{uuid.uuid4().hex}.{ext}"
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)
        path = os.path.join(upload_dir, stored)

        f.save(path)

        # 🔐 vérification de la signature MIME
        detected = _check_magic(path)
        if detected is None or detected not in current_app.config["ALLOWED_MIME_TYPES"]:
            os.remove(path)
            flash("Type de fichier non autorisé (signature invalide).", "danger")
            return redirect(url_for("documents.upload"))

        # 🔐 hash d'intégrité
        with open(path, "rb") as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()

        d = Document(
            title=title[:200],
            original_filename=original,
            stored_filename=stored,
            mime_type=detected,
            file_size=os.path.getsize(path),
            sha256=sha,
            owner_user_id=current_user.id,
        )
        db.session.add(d)
        db.session.commit()
        flash("Document téléversé.", "success")
        return redirect(url_for("documents.index"))

    return render_template("documents/upload.html")


@documents_bp.route("/download/<int:doc_id>")
@login_required
def download(doc_id):
    """🔐 Téléchargement par ID, pas par nom de fichier."""
    doc = Document.query.get_or_404(doc_id)

    # Contrôle d'accès
    if not (doc.is_public
            or doc.owner_user_id == current_user.id
            or current_user.has_role("admin", "academic_manager")):
        abort(403)

    upload_dir = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
    try:
        # 🔐 safe_join empêche toute évasion hors du dossier
        full = safe_join(upload_dir, doc.stored_filename)
    except Exception:
        abort(400)

    if not full or not os.path.isfile(full):
        abort(404)

    # 🔐 vérification finale : le chemin résolu est bien dans upload_dir
    real = os.path.realpath(full)
    if not real.startswith(os.path.realpath(upload_dir) + os.sep):
        abort(403)

    return send_file(
        real,
        mimetype=doc.mime_type or "application/octet-stream",
        as_attachment=True,
        download_name=doc.original_filename,  # nom original restitué
    )


@documents_bp.route("/preview/<int:doc_id>")
@login_required
def preview(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if not (doc.is_public
            or doc.owner_user_id == current_user.id
            or current_user.has_role("admin", "academic_manager")):
        abort(403)
    return render_template("documents/preview.html", doc=doc)