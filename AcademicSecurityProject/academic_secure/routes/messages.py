from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.message import Message
from models.user import User

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/")
@login_required
def inbox():
    items = (Message.query
             .filter_by(recipient_id=current_user.id)
             .order_by(Message.created_at.desc()).all())
    return render_template("messages/list.html", messages=items, box="inbox")


@messages_bp.route("/sent")
@login_required
def sent():
    items = (Message.query
             .filter_by(sender_id=current_user.id)
             .order_by(Message.created_at.desc()).all())
    return render_template("messages/list.html", messages=items, box="sent")


@messages_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    users = User.query.filter(User.id != current_user.id).all()
    if request.method == "POST":
        try:
            rid = int(request.form.get("recipient_id", "0"))
        except ValueError:
            rid = 0
        recipient = User.query.get(rid)
        if not recipient:
            flash("Destinataire invalide.", "danger")
            return redirect(url_for("messages.new"))
        m = Message(subject=(request.form.get("subject") or "")[:200],
                    body=(request.form.get("body") or "")[:10000],
                    sender=current_user, recipient=recipient)
        db.session.add(m)
        db.session.commit()
        flash("Message envoyé.", "success")
        return redirect(url_for("messages.sent"))
    return render_template("messages/form.html", users=users)