# AcademicSecurityProject

Deux applications Flask de gestion académique développées pour un TP universitaire
de **sécurité applicative**. Elles sont **identiques sur le plan fonctionnel** mais
divergent **uniquement sur le plan sécurité** :

- **`academic_vulnerable/`** — Application A, contient volontairement des faiblesses
  pour illustrer les 14 missions du TP (XSS, SQLi, path traversal, JWT faible, etc.).
- **`academic_secure/`** — Application B, mêmes fonctionnalités, avec toutes les
  contre-mesures en place.

⚠️ **Usage strictement pédagogique et local.** Les scénarios dangereux sont simulés
et confinés dans `laboratory/`. Ne jamais exposer ces applications à Internet.

---

## 📚 Sommaire

- [Objectifs](#-objectifs)
- [Technologies](#-technologies)
- [Structure](#-structure)
- [Installation rapide](#-installation-rapide)
- [Lancement](#-lancement)
- [Tests](#-tests)
- [Les 14 missions de sécurité](#-les-14-missions-de-sécurité)
- [Documentation détaillée](#-documentation-détaillée)
- [Limites du laboratoire](#-limites-du-laboratoire)

---

## 🎯 Objectifs

1. Développer une application académique **complète et fonctionnelle**
   (utilisateurs, rôles, étudiants, enseignants, cours, notes, documents, annonces…).
2. Reproduire dans un **environnement isolé** 14 vulnérabilités courantes (OWASP).
3. Fournir pour chacune une **contre-mesure** dans la version sécurisée.
4. Produire des **preuves comparatives** utilisables pour la soutenance.

## 🛠 Technologies

| Couche | Outils |
|--------|--------|
| Backend | Python 3, Flask 3, Flask-SQLAlchemy, Flask-Login, Flask-WTF, PyJWT |
| Base de données | SQLite 3 |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons, Chart.js, Jinja2 |
| Hash (secure) | Argon2id via `argon2-cffi` |
| Hash (vuln) | SHA-256 non salé (démo Mission 1.13) |
| Tests | pytest, pytest-flask |
| Déploiement | Nginx, Gunicorn (Ubuntu) |

## 📁 Structure
