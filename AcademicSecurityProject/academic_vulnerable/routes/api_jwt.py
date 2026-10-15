import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

"""
Routes JWT additionnelles (si tu veux les séparer).
Les routes JWT principales sont dans routes/auth.py.
"""
# Vide pour l'instant — les routes /api/token et /api/me sont dans auth.py