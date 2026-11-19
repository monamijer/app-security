# 🛡️ Guide Officiel de Démonstration — 14 Missions de Sécurité Applicative

Ce document rassemble l'ensemble des attaques, contre-mesures, commandes de test et résultats attendus pour la soutenance du TP de Sécurité Applicative devant le professeur.

---

## 🌐 0. Environnement & Topologie de Démonstration

```text
┌───────────────────────────────────────┐         ┌───────────────────────────────────────┐
│     MACHINE 1 : SERVEUR CIBLE         │         │     MACHINE 2 : AUDITEUR / ATTAQUANT  │
│     OS  : Windows                     │  Wi-Fi  │     OS  : Arch Linux                  │
│     IP  : 192.168.0.225               │◄───────►│     IP  : 192.168.0.x                 │
│     - Port 8080 : App Vulnérable      │         │     - Outils : curl, openssl, netcat, │
│     - Port 8081 : App Sécurisée (TLS) │         │       firefox, testssl, python        │
└───────────────────────────────────────┘         └───────────────────────────────────────┘
```

### Initialisation des variables sur Arch Linux
À exécuter une seule fois au début de la session dans le terminal Arch Linux :

```bash
export SERVER_IP="192.168.0.225"
export VULN="http://${SERVER_IP}:8080"
export SECURE="https://${SERVER_IP}:8081"

# Vérification rapide de connectivité :
curl -sS -o /dev/null -w "App Vulnérable (8080) : %{http_code}\n" "$VULN/"
curl -k -sS -o /dev/null -w "App Sécurisée (8081)  : %{http_code}\n" "$SECURE/"
```

---

## 🎯 1. Les 14 Missions Pas à Pas

---

### Mission 1.1 — Audit Global des En-têtes HTTP de Sécurité

* **Objectif :** Démontrer l'absence de défense en profondeur sur l'application vulnérable et la présence des en-têtes durcis sur l'application sécurisée.
* **Ce que fait l'attaque :** Une simple requête d'inspection (`HEAD`) interroge les en-têtes renvoyés par le serveur web avant toute négociation de contenu.

#### Test 1 — Côté Vulnérable
```bash
curl -sSI "$VULN/" | grep -iE '^(HTTP/|content-security-policy:|x-frame-options:|strict-transport-security:|x-content-type-options:|referrer-policy:|cross-origin-opener-policy:|cross-origin-embedder-policy:|permissions-policy:)'
```
* **Résultat attendu :** Seul le code `HTTP/1.1 200 OK` (ou 302) apparaît. **Aucun en-tête de protection** n'est présent.

#### Test 2 — Côté Sécurisé
```bash
curl -k -sSI "$SECURE/" | grep -iE '^(HTTP/|content-security-policy:|x-frame-options:|strict-transport-security:|x-content-type-options:|referrer-policy:|cross-origin-opener-policy:|cross-origin-embedder-policy:|permissions-policy:)'
```
* **Résultat attendu :** Affichage complet des 8 en-têtes de sécurité :
  - `Content-Security-Policy: default-src 'self'; ...`
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: camera=(), microphone=(), geolocation=()`
  - `Cross-Origin-Opener-Policy: same-origin`
  - `Cross-Origin-Embedder-Policy: require-corp`
* **Statut :** **CONFIRMED**

---

### Mission 1.2 — Transport Sécurisé TLS & Protection HSTS

* **Objectif :** Prouver la transmission en clair sur le port 8080 (sensible au sniffing et SSL Stripping) et le chiffrement fort avec certificat persistant et HSTS sur le port 8081.
* **Ce que fait le test :** Établissement d'une négociation TLS via `openssl` pour vérifier la cryptographie asymétrique et les identités SAN du certificat.

#### Test 1 — Vérification du port 8080 (Non chiffré)
```bash
curl -sSI "$VULN/" | head -n 5
```
* **Résultat attendu :** Réponse HTTP simple en clair, aucune couche de chiffrement.

#### Test 2 — Négociation TLS sur le port 8081
```bash
openssl s_client -connect "${SERVER_IP}:8081" -servername secure.local </dev/null
```
* **Résultat attendu :** La négociation TLS 1.2/1.3 réussit. Affichage du certificat `CN=secure.local`, `O=AcademicLab`, avec validation de l'IP alternative `192.168.0.225` dans le Subject Alternative Name (SAN).
* **Statut :** **CONFIRMED**

---

### Mission 1.3 — Injection XSS Réfléchie (Reflected XSS)

* **Objectif :** Démontrer l'injection de scripts arbitraires via le paramètre de recherche non échappé (`Markup(q)`), puis son neutralisation par l'échappement contextuel automatique et la CSP.
* **Ce que fait l'attaque :** L'attaquant insère du code JavaScript `<script>alert('LAB-XSS')</script>` dans l'URL. Si l'application réinjecte cette valeur sans conversion en entités HTML, le navigateur l'exécute.

#### Test 1 — Côté Vulnérable
```bash
curl -sS -G --data-urlencode "q=<script>alert('LAB-XSS')</script>" "$VULN/search" | grep -inE 'script|&lt;|alert'
```
* **Résultat attendu :** Le script est retourné **brut dans le code source HTML** :
  ```html
  <strong><script>alert('LAB-XSS')</script></strong>
  ```
  *(Dans le navigateur, une boîte d'alerte surgit immédiatement).*

#### Test 2 — Côté Sécurisé
```bash
curl -k -sS -G --data-urlencode "q=<script>alert('LAB-XSS')</script>" "$SECURE/search" | grep -inE 'script|&lt;|alert'
```
* **Résultat attendu :** Les caractères dangereux sont automatiquement neutralisés en entités HTML :
  ```html
  <strong>&lt;script&gt;alert(&#39;LAB-XSS&#39;)&lt;/script&gt;</strong>
  ```
  *(Le script s'affiche comme du simple texte inoffensif, et la CSP bloque toute tentative).*
* **Statut :** **CONFIRMED**

---

### Mission 1.4 — Protection contre le Clickjacking (UI Redressing)

* **Objectif :** Tenter d'encadrer l'application dans une `<iframe>` invisible pour piéger les clics de l'utilisateur.
* **Ce que fait l'attaque :** Un site attaquant intègre la cible dans une balise `<iframe>` transparente superposée à un faux bouton.

#### Test sur Arch Linux
```bash
mkdir -p ~/audit-lab
cat > ~/audit-lab/clickjack.html <<EOF
<!doctype html>
<html>
<head><meta charset="utf-8"><title>PoC Clickjacking</title></head>
<body>
  <h2>Test Clickjacking Iframe</h2>
  <h3>Cible 1 : Application Vulnérable</h3>
  <iframe src="$VULN/" width="800" height="400"></iframe>
  <h3>Cible 2 : Application Sécurisée</h3>
  <iframe src="$SECURE/" width="800" height="400"></iframe>
</body>
</html>
EOF

firefox ~/audit-lab/clickjack.html
```
* **Résultat attendu :**
  - **Cadre vulnérable :** L'application se charge normalement à l'intérieur du cadre.
  - **Cadre sécurisé :** Firefox bloque le chargement et affiche une erreur de sécurité grâce à `X-Frame-Options: DENY` et CSP `frame-ancestors 'none'`.
* **Statut :** **CONFIRMED**

---

### Mission 1.5 — Reniflage de Type MIME (MIME Sniffing)

* **Objectif :** Empêcher les navigateurs de deviner le type de contenu d'un fichier et d'exécuter un fichier piégé (polyglotte).
* **Ce que fait le test :** Vérification de l'instruction stricte `nosniff`.

#### Test
```bash
printf '\n=== VULNERABLE ===\n'
curl -sSI "$VULN/" | grep -i '^X-Content-Type-Options:' || echo "En-tête absent"

printf '\n=== SECURE ===\n'
curl -k -sSI "$SECURE/" | grep -i '^X-Content-Type-Options:' || echo "En-tête absent"
```
* **Résultat attendu :**
  - Vulnérable : Aucun en-tête (le navigateur peut interpréter un script caché dans une image).
  - Sécurisé : `X-Content-Type-Options: nosniff` (le navigateur respecte strictement le type MIME déclaré).
* **Statut :** **CONFIRMED**

---

### Mission 1.6 — Fuite de Données Sensibles via Referrer (Referrer Leakage)

* **Objectif :** Éviter que des jetons ou paramètres d'URL confidentiels ne soient transmis à des sites tiers lors du clic sur un lien sortant.
* **Ce que fait l'attaque :** L'utilisateur navigue sur une page contenant un secret d'authentification dans l'URL (`?token=SECRET_ADMIN_TOKEN_999`). En cliquant sur un lien externe, le navigateur sans politique restrictive inclut l'URL complète dans l'en-tête HTTP `Referer`.

#### Déroulement du Test
1. **Sur Arch Linux**, lancer le serveur d'écoute en arrière-plan pour capturer l'en-tête `Referer` :
   ```bash
   # Micro-serveur d'écoute Python (100% fiable, ne se coupe pas) :
    python3 -c '
    from http.server import HTTPServer, BaseHTTPRequestHandler
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            print("\n" + "="*40)
            print("🎯 REQUÊTE CAPTURÉE !")
            print("Path    :", self.path)
            print("Referer :", self.headers.get("Referer", "(aucun)"))
            print("="*40 + "\n")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK CAPTURE")
    print("Écoute active sur le port 9999...")
    HTTPServer(("0.0.0.0", 9999), Handler).serve_forever()
    '
       '
   ```
   *(Alternative Netcat si installé : `nc -l -k -p 9999` ou `ncat -l -k 9999`)*.

2. **Dans le navigateur sur Arch Linux**, ouvrir l'URL vulnérable :
   ```text
   http://192.168.0.225:8080/referrer-leak?token=SECRET_ADMIN_TOKEN_999
   ```
3. Cliquer sur le bouton **« Cliquer vers le serveur externe de test »** :
   * **Résultat Vulnérable :** Le terminal affiche :
     ```text
     Referer : http://192.168.0.225:8080/referrer-leak?token=SECRET_ADMIN_TOKEN_999
     ```
     👉 **Preuve de la fuite :** Le paramètre secret `token` a été transmis en clair au serveur externe tiers.

4. **Dans le navigateur**, ouvrir maintenant l'URL sécurisée :
   ```text
   https://192.168.0.225:8081/referrer-leak?token=SECRET_ADMIN_TOKEN_999
   ```
5. Cliquer sur le bouton externe sécurisé :
   * **Résultat Sécurisé :** Le terminal affiche :
     ```text
     Referer : https://192.168.0.225:8081/
     ```
     👉 **Preuve du blocage :** Grâce à `Referrer-Policy: strict-origin-when-cross-origin`, seul le nom de domaine de l'origine est transmis. Le chemin et le token secret sont **totalement masqués**.

* **Statut :** **CONFIRMED**

---

### Mission 1.7 — Isolation de Processus Navigateur (COOP & COEP)

* **Objectif :** Isoler le document dans son propre groupe de contexte de navigation pour empêcher les attaques de canal auxiliaire (ex: Spectre) et les fuites via `window.opener`.

#### Test
```bash
printf '\n=== VULNERABLE ===\n'
curl -sSI "$VULN/" | grep -iE '^Cross-Origin-(Opener|Embedder)-Policy:' || echo "COOP/COEP absent"

printf '\n=== SECURE ===\n'
curl -k -sSI "$SECURE/" | grep -iE '^Cross-Origin-(Opener|Embedder)-Policy:' || echo "COOP/COEP absent"
```
* **Résultat attendu :**
  - Vulnérable : Absence totale de politique d'isolation.
  - Sécurisé :
    ```text
    Cross-Origin-Opener-Policy: same-origin
    Cross-Origin-Embedder-Policy: require-corp
    ```
* **Statut :** **CONFIRMED**

---

### Mission 1.8 — Restriction des Fonctionnalités Matérielles (Permissions-Policy)

* **Objectif :** Désactiver au niveau du navigateur l'accès aux capteurs sensibles (micro, caméra, géolocalisation) pour empêcher leur exploitation par du code tiers injecté.

#### Test
```bash
curl -k -sSI "$SECURE/" | grep -i '^Permissions-Policy:'
```
* **Résultat attendu :**
  ```text
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  ```
* **Statut :** **CONFIRMED**

---

### Mission 1.9 — Injection SQL (SQL Injection)

* **Objectif :** Exploiter la concaténation directe de chaîne SQL pour exfiltrer l'intégralité de la base de données, puis démontrer la neutralisation par requêtes paramétrées ORM.
* **Ce que fait l'attaque :** Le payload `' OR 1=1 --` ferme la clause de recherche et ajoute une condition toujours vraie, court-circuitant le reste de la requête avec un commentaire SQL `--`.

#### Test 1 — Côté Vulnérable (Extraction de la base)
```bash
printf '\n=== 1. RECHERCHE NORMALE (admin) ===\n'
curl -sS -G --data-urlencode 'q=admin' "$VULN/api/search"

printf '\n=== 2. INJECTION SQL (DUMP DES 28 UTILISATEURS) ===\n'
curl -sS -G --data-urlencode "q=' OR 1=1 --" "$VULN/api/search"
```
* **Résultat attendu :**
  - Recherche normale : 1 seul résultat (`admin`).
  - Injection SQL : La requête retourne **la totalité des 28 utilisateurs de l'université** (admin, responsables, enseignants, étudiants).

#### Test 2 — Côté Sécurisé (Requête Paramétrée)
```bash
printf '\n=== 3. TENTATIVE D INJECTION SUR APPLICATION SÉCURISÉE ===\n'
curl -k -sS -G --data-urlencode "q=' OR 1=1 --" "$SECURE/api/search"
```
* **Résultat attendu :**
  ```json
  {"query": "' OR 1=1 --", "results": []}
  ```
  *(L'ORM SQLAlchemy traite `' OR 1=1 --` comme une chaîne de caractères littérale à rechercher, neutralisant toute modification de la grammaire SQL).*
* **Statut :** **CONFIRMED**

---

### Mission 1.10 — Injection de Commandes OS (OS Command Injection)

* **Objectif :** Exécuter une commande système arbitraire sur le serveur d'arrière-plan via un champ de diagnostic ping mal sécurisé.
* **Ce que fait l'attaque :** L'attaquant injecte un séparateur de commandes (`;` sous Linux ou `&` sous Windows) pour exécuter une commande arbitraire (`echo LAB_COMMAND_MARKER`).

#### Test 1 — Côté Vulnérable
```bash
curl -sS -X POST "$VULN/diagnostics" \
  --data-urlencode 'target=127.0.0.1;echo LAB_COMMAND_MARKER' | grep -i "LAB_COMMAND_MARKER"
```
* **Résultat attendu :** La réponse HTML contient la ligne de sortie du terminal exécutée :
  ```text
  LAB_COMMAND_MARKER
  ```
  *(Preuve formelle d'exécution de code sur le système d'exploitation hôte).*

#### Test 2 — Côté Sécurisé
```bash
curl -k -sS -i -X POST "$SECURE/diagnostics" \
  --data-urlencode 'target=127.0.0.1;echo LAB_COMMAND_MARKER' | head -n 12
```
* **Résultat attendu :** Rejet immédiat (`HTTP 400` ou `HTTP 302` redirection login). Si authentifié, le validateur d'adresses strict `ipaddress.ip_address()` rejette tout caractère non numérique avec le message :
  `"Adresse refusée. Seules les IP privées ou loopback sont autorisées."`
  *(Aucun appel shell n'est effectué : `shell=False`, argument listé).*
* **Statut :** **CONFIRMED**

---

### Mission 1.11 — XSS Stocké & Vol de Session (Stored XSS)

* **Objectif :** Insérer un script persistant dans la base de données via un commentaire ou une annonce qui s'exécutera auprès de chaque utilisateur consultant la page.

#### Démonstration
1. Se connecter sur `http://192.168.0.225:8080/login` (`admin` / `Admin@2025!`).
2. Créer une annonce avec le contenu inoffensif : `<script>alert('LAB-XSS')</script>`.
3. **Côté Vulnérable :** Le template utilise `| safe` et les cookies n'ont pas `HttpOnly`. Le script s'exécute à chaque chargement de la page d'accueil.
4. **Côté Sécurisé :** Le template applique l'échappement Jinja2 strict et les cookies de session sont protégés par `HttpOnly; SameSite=Lax`. Le script apparaît comme du texte inoffensif.
* **Statut :** **CONFIRMED**

---

### Mission 1.12 — Traversée de Répertoire (Path Traversal)

* **Objectif :** Sortir du dossier prévu pour les téléchargements afin de lire un fichier système confidentiel sur le serveur.
* **Ce que fait l'attaque :** Utilisation des séquences `%2e%2e%2f` (`../`) pour remonter l'arborescence des fichiers.

#### Test 1 — Côté Vulnérable
Le fichier témoin `static/LAB-TRAVERSAL.txt` a été placé sur le serveur :
```bash
curl -i --path-as-is "$VULN/documents/download/%2e%2e%2fLAB-TRAVERSAL.txt"
```
* **Résultat attendu :**
  ```text
  HTTP/1.1 200 OK
  Content-Disposition: attachment; filename=LAB-TRAVERSAL.txt

  PATH_TRAVERSAL_CONFIRMED
  ```
  *(Le serveur a permis d'extraire un fichier en dehors du répertoire d'upload).*

#### Test 2 — Côté Sécurisé
```bash
curl -k -i --path-as-is "$SECURE/documents/download/%2e%2e%2fLAB-TRAVERSAL.txt"
```
* **Résultat attendu :** `HTTP 404 NOT FOUND`.
  *(L'application sécurisée impose un identifiant entier numérique `/download/<int:doc_id>`, applique `safe_join()`, et vérifie les permissions en base de données).*
* **Statut :** **CONFIRMED**

---

### Mission 1.13 — Robustesse des Fonctions de Hachage

* **Objectif :** Comparer la résistance des mots de passe hachés stockés en base face aux attaques par dictionnaire et GPU.

#### Inspection du Code Source
```bash
# App Vulnérable :
grep -nE 'generate_password_hash|pbkdf2|salt_length' \
  AcademicSecurityProject/academic_vulnerable/models/user.py

# App Sécurisée :
grep -nE 'PasswordHasher|time_cost|memory_cost|parallelism|argon2' \
  AcademicSecurityProject/academic_secure/models/user.py
```
* **Constat Vulnérable :** `pbkdf2:sha256:1` avec un sel de seulement 4 octets. Une seule itération de hachage permet un cassage quasi-instantané avec Hashcat / John the Ripper.
* **Constat Sécurisé :** Utilisation de l'algorithme vainqueur du Password Hashing Competition **Argon2id** (`time_cost=3`, `memory_cost=65536` [64 Mo de RAM], `parallelism=2`), résistant aux accélérateurs matériels GPU et ASIC.
* **Statut :** **CONFIRMED**

---

### Mission 1.14 — Falsification de Jetons JWT (JWT Tampering)

* **Objectif :** Démontrer l'usurpation de privilèges (passer d'un compte étudiant à admin) grâce à une clé secrète faible connue, puis vérifier le rejet strict par signature et vérification en base.

#### Test 1 — Obtention d'un jeton légitime (Étudiant)
```bash
  RAW=$(curl -s -X POST "$VULN/api/token" \
    -H "Content-Type: application/json" \
    -d '{"username": "student1", "password": "Student@2025!1"}')

TOKEN=$(printf '%s' "$RAW" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('token') or d.get('access_token') or '')")
echo "$TOKEN"
# Consultation du profil :
curl -s -H "Authorization: Bearer $TOKEN" "$VULN/api/me"
# -> {"role": "student", "user_id": 9}
```

#### Test 2 — Rejet sur l'Application Sécurisée
```bash
# Tentative avec un jeton forgé ou signature altérée :
curl -k -s -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0.FAKESIGNATURE" \
  "$SECURE/api/me"
```
* **Résultat attendu :**
  ```json
  {"error": "invalid_token"}
  ```
  *(HTTP 401 Unauthorized : signature rejetée et le rôle est toujours revalidé en base via `User.query.get(sub)`).*
* **Statut :** **CONFIRMED**

---

## 📊 2. Grille d'Évaluation Complète pour le Professeur

| Mission | Nom de l'Attaque | Comportement Vulnérable (Port 8080) | Contre-mesure Sécurisée (Port 8081) | Statut |
|:---:|---|---|---|:---:|
| **1.1** | Audit En-têtes HTTP | 0 en-tête de protection | 8 en-têtes durcis (CSP, HSTS, XFO...) | **CONFIRMED** |
| **1.2** | Downgrade / Transport | HTTP en clair | TLS 1.2/1.3 + HSTS max-age 1 an | **CONFIRMED** |
| **1.3** | Reflected XSS | Injection directe `<script>` | Échappement HTML `&lt;` + CSP strict | **CONFIRMED** |
| **1.4** | Clickjacking | Iframe transparente autorisée | `X-Frame-Options: DENY` | **CONFIRMED** |
| **1.5** | MIME Sniffing | Risque de mauvaise interprétation | `X-Content-Type-Options: nosniff` | **CONFIRMED** |
| **1.6** | Referrer Leak | Token d'URL exposé à l'extérieur | Masquage `strict-origin` | **CONFIRMED** |
| **1.7** | COOP & COEP | Aucune barrière de processus | `same-origin` & `require-corp` | **CONFIRMED** |
| **1.8** | Permissions-Policy | Accès capteurs illimité | Caméra, micro, GPS désactivés | **CONFIRMED** |
| **1.9** | SQL Injection | **28 comptes utilisateurs dumpés** | 0 résultat (ORM paramétré) | **CONFIRMED** |
| **1.10** | OS Command Injection | **Code système exécuté** (`MARKER`) | Rejet strict (`ipaddress` + `shell=False`) | **CONFIRMED** |
| **1.11** | Stored XSS | Script persistant exécuté | Échappement template + cookies HttpOnly | **CONFIRMED** |
| **1.12** | Path Traversal | Fichier confidentiel téléchargé | 404 (ID numérique + `safe_join`) | **CONFIRMED** |
| **1.13** | Password Hashing | PBKDF2 faible (1 itération, sel 4) | Argon2id moderne (64 Mo RAM) | **CONFIRMED** |
| **1.14** | JWT Security | Rôle altéré accepté | Rejet signature & relecture DB | **CONFIRMED** |
