"""
Réinitialise les bases SQLite de laboratoire.
⚠️ Efface toutes les données. À n'utiliser qu'en environnement isolé.

Usage :
    python database/reset_database.py both
    python database/reset_database.py vulnerable
    python database/reset_database.py secure
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def reset(app_name: str) -> None:
    app_dir = os.path.join(ROOT, f"academic_{app_name}")
    instance_dir = os.path.join(app_dir, "instance")
    db_file = os.path.join(instance_dir, f"academic_{app_name}.db")

    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"🗑️  Supprimé : {db_file}")
    else:
        print(f"ℹ️  Introuvable (déjà absent) : {db_file}")

    print(f"➡️  Pour recréer les données : python database/seed.py {app_name}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "both"
    if target in ("vulnerable", "both"):
        reset("vulnerable")
    if target in ("secure", "both"):
        reset("secure")