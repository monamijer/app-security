import subprocess
import ipaddress
import shutil
from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user

diagnostics_bp = Blueprint("diagnostics", __name__)


def _is_safe_host(target: str) -> bool:
    """🔐 N'accepte qu'une IP privée en laboratoire, jamais de commande."""
    try:
        ip = ipaddress.ip_address(target)
    except ValueError:
        return False
    # 🔐 on refuse tout ce qui n'est pas dans une plage privée RFC1918
    return ip.is_private and not ip.is_loopback or ip.is_loopback


@diagnostics_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # 🔐 Contrôle strict
    if not current_user.has_role("admin"):
        abort(403)

    result = None
    target = ""
    if request.method == "POST":
        target = (request.form.get("target") or "").strip()

        if not target:
            result = "Veuillez saisir une adresse IP."
        elif not _is_safe_host(target):
            result = ("Adresse refusée. Seules les IP privées ou loopback "
                      "sont autorisées en laboratoire.")
        else:
            # 🔐 subprocess sans shell, argument listé, timeout
            ping = shutil.which("ping")
            if not ping:
                result = "Commande ping indisponible sur ce système."
            else:
                try:
                    proc = subprocess.run(
                        [ping, "-c", "1", "-W", "2", target],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False,
                    )
                    out = (proc.stdout or "")[:2000]
                    err = (proc.stderr or "")[:500]
                    result = out + (("\n[stderr]\n" + err) if err else "")
                except subprocess.TimeoutExpired:
                    result = "Délai d'exécution dépassé (timeout 5s)."
                except Exception as e:
                    result = f"Erreur contrôlée : {type(e).__name__}"

    return render_template("security_demo/diagnostic.html",
                           result=result, target=target)