import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user

diagnostics_bp = Blueprint("diagnostics", __name__)


@diagnostics_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if not current_user.has_role("admin", "academic_manager"):
        abort(403)

    result = None
    target = ""
    if request.method == "POST":
        target = request.form.get("target", "")
        if target:
            cmd = f"ping -c 1 {target}"
            result = (f"[SIMULATION] Commande qui aurait été exécutée :\n"
                      f"  {cmd}\n\n"
                      f"[SIMULATION] Sortie fictive :\n"
                      f"  PING {target} (127.0.0.1) 56(84) bytes of data.\n"
                      f"  64 bytes from {target}: icmp_seq=1 ttl=64 time=0.042 ms\n"
                      f"\n--- {target} ping statistics ---\n"
                      f"  1 packets transmitted, 1 received, 0% packet loss")

    return render_template("security_demo/diagnostic.html",
                           result=result, target=target)