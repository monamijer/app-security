from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db
from models.announcement import Announcement
from models.comment import Comment

announcements_bp = Blueprint("announcements", __name__)


@announcements_bp.route("/")
@login_required
def index():
    items = Announcement.query.filter_by(is_published=True)\
        .order_by(Announcement.created_at.desc()).all()
    return render_template("announcements/list.html", announcements=items)


@announcements_bp.route("/<int:ann_id>", methods=["GET", "POST"])
@login_required
def detail(ann_id):
    ann = Announcement.query.get_or_404(ann_id)

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            # ⚠️ Vulnérable : contenu HTML conservé brut
            db.session.add(Comment(content=content, author=current_user,
                                   announcement=ann))
            db.session.commit()
            flash("Commentaire publié.", "success")
        return redirect(url_for("announcements.detail", ann_id=ann.id))

    return render_template("announcements/detail.html", announcement=ann)


@announcements_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if not current_user.has_role("admin", "academic_manager", "teacher"):
        abort(403)
    if request.method == "POST":
        ann = Announcement(
            title=request.form.get("title", "")[:200],
            content=request.form.get("content", ""),
            author=current_user,
        )
        db.session.add(ann)
        db.session.commit()
        flash("Annonce publiée.", "success")
        return redirect(url_for("announcements.index"))
    return render_template("announcements/form.html")