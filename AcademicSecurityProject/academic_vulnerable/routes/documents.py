import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, abort, send_file, current_app)
from flask_login import login_required, current_user

from models import db
from models.document import Document

documents_bp = Blueprint("documents", __name__)


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
        title = request.form.get("title", "")
        if not f or not f.filename:
            flash("Aucun fichier.", "danger")
            return redirect(url_for("documents.upload"))

        filename = f.filename
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)
        path = os.path.join(upload_dir, filename)
        f.save(path)

        d = Document(title=title, filename=filename, filepath=path,
                     mime_type=f.mimetype, file_size=os.path.getsize(path),
                     owner_user_id=current_user.id)
        db.session.add(d)
        db.session.commit()
        flash("Document téléversé.", "success")
        return redirect(url_for("documents.index"))

    return render_template("documents/upload.html")


@documents_bp.route("/download/<path:filename>")
@login_required
def download(filename):
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    full = os.path.join(upload_dir, filename)
    if not os.path.exists(full):
        abort(404)
    return send_file(full, as_attachment=True)


@documents_bp.route("/preview/<int:doc_id>")
@login_required
def preview(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return render_template("documents/preview.html", doc=doc)