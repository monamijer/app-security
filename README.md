# Academic Security Project — School Management System

A Bachelor 2 application-security project developed by two students using **Python and Flask**. The project compares two functionally equivalent School Management System applications: one intentionally vulnerable and one hardened.

- **Vulnerable application:** demonstrates selected weaknesses in a controlled academic laboratory.
- **Secure application:** applies defensive controls and must reject or safely handle the same test cases.

> **Safety:** This is an educational security lab, not a production application. Use synthetic accounts and records only. Keep the vulnerable instance on an isolated trusted network; never expose it to the public internet. Test only the two systems explicitly authorized for this project.

## Project objectives

1. Maintain one realistic School Management System with equivalent features in both versions.
2. Demonstrate the 14 security missions required by the instructor against the vulnerable version or through explicitly harmless simulations.
3. Implement and verify the corresponding defenses in the secure version.
4. Preserve repeatable test cases and sanitized evidence for the final report and oral defense.
5. Explain the root cause, impact, mitigation, and test result for every mission.

## Technology and environment

| Component | Current project choice |
|---|---|
| Backend | Python 3, Flask 3 |
| ORM / database | Flask-SQLAlchemy, SQLite |
| Authentication | Flask-Login, Flask-WTF, PyJWT |
| Secure password hashing | Argon2id (argon2-cffi) |
| Vulnerable password hashing | PBKDF2-SHA256 configured with one iteration and a short salt (intentionally weak) |
| Frontend | Jinja2, HTML, CSS, JavaScript, Bootstrap |
| Tests | pytest, pytest-flask |
| Reverse proxy configuration | Nginx configuration files are present |
| Attacker workstation | Arch Linux |
| Application host | Windows laptop (as reported by the project team) |
| Team | Two students |

The repository contains Nginx configuration written with Linux paths and deployment assumptions. The Windows deployment must be checked separately; do not assume the checked-in Nginx configuration runs unchanged on Windows.

## Applications and reported lab endpoints

| Service | Reported address | Purpose |
|---|---|---|
| Vulnerable | http://192.168.137.200:8080 | Controlled vulnerability demonstrations |
| Secure | https://192.168.137.200:8081 | Defensive comparison |

These addresses and the observed HTTP/TLS behavior were supplied by the project team. They are **reported runtime observations**, not verified by reading the source code in this repository.

### Deployment configuration needs reconciliation

The checked-in files currently describe different listener and upstream ports:

- **academic_vulnerable/app.py** runs on **127.0.0.1:8080** when launched directly.
- **academic_secure/app.py** runs on **127.0.0.1:8081** when launched directly.
- **nginx/vulnerable.conf** listens on **8080** and proxies to **127.0.0.1:5000**.
- **nginx/secure.conf** listens on **443** and proxies to **127.0.0.1:5001**.

These are not one consistent deployment configuration. Before changing ports or giving launch commands, verify the actual Windows processes, reverse proxy, and port bindings with the teammate who hosts the applications.

The secure Nginx configuration references **secure.local** and certificate files under **/etc/nginx/ssl/**. The team has reported using a self-signed certificate whose SAN does not include **192.168.137.200**. A proper lab certificate must include the exact IP address in its IP Subject Alternative Name (or use a DNS name consistently), and the issuing lab CA must be trusted on the Arch Linux attacker machine. Until then, **curl -k** is only for temporary diagnostics; it disables certificate verification and does not establish trusted HTTPS.

## Repository structure

The main application project is under **AcademicSecurityProject/**.

    app-security/
    ├── AcademicSecurityProject/
    │   ├── academic_vulnerable/     # Intentionally vulnerable Flask application
    │   ├── academic_secure/         # Hardened Flask application
    │   ├── shared/                  # Shared academic helper/validation logic
    │   ├── laboratory/              # Project laboratory evidence
    │   └── README.md                # Application-project documentation (French)
    ├── database/
    │   ├── seed.py                  # Creates matching synthetic datasets
    │   └── reset_database.py
    ├── documentation/               # Architecture, testing, and comparison docs
    ├── laboratory/                  # Evidence, fixtures, test cases, sample files
    ├── nginx/
    │   ├── vulnerable.conf
    │   └── secure.conf
    └── README.md

Both applications include modules for authentication, administration, students, teachers, courses, grades, documents, announcements, messages, diagnostics, models, services, templates, static assets, and tests.

## The 14 required security missions

The table below is an initial source-code review, not a claim that all missions have passed practical testing. “Partial” means that relevant code or configuration exists, but the complete instructor-required demonstration and secure comparison still need evidence. Re-test every behavior in the running lab.

| Mission | Topic and required tool / technique | Initial source review |
|---|---|---|
| 1.1 | Security audit and missing headers — Nikto | **Implemented in code/config:** vulnerable app adds no security headers; secure app defines CSP, X-Frame-Options, nosniff, and related headers. Runtime verification still required. |
| 1.2 | Transport security and downgrade — testssl.sh / bettercap | **Partial:** secure Nginx config specifies TLS 1.2/1.3 and HSTS. Listener/port and certificate identity mismatch must be resolved; TLS scan evidence is still required. |
| 1.3 | Reflected and stored XSS / CSP — XSStrike | **Partial:** vulnerable search output and announcement/comment templates contain unsafe rendering. Secure search and comment rendering use normal Jinja escaping, but the secure announcement template still uses the safe filter for announcement content. |
| 1.4 | Clickjacking — HTML proof of concept | **Partial:** secure X-Frame-Options and CSP frame-ancestors are configured. The dedicated PoC and browser evidence still need to be created and tested. |
| 1.5 | Polyglot upload and MIME sniffing — hexadecimal test file | **Partial:** vulnerable upload trusts the supplied filename and MIME metadata; secure upload checks extension and file signature and stores files outside static assets. Full browser/MIME test evidence is still required. |
| 1.6 | Referer leakage — Wireshark | **Partial:** Referrer-Policy is configured in the secure version. A synthetic sensitive-URL demonstration and packet evidence are still required. |
| 1.7 | Cross-window attacks / information leakage — window.open() PoC | **Partial:** COOP is configured. COEP is not present in the reviewed secure header configuration; cross-window PoC and browser verification remain. |
| 1.8 | Browser hardware permissions — BeEF | **Partial:** secure Permissions-Policy denies camera, microphone, and geolocation. A harmless, explicit-permission browser demonstration and verification remain. |
| 1.9 | SQL injection — SQLmap | **Known blocker:** vulnerable authentication and search code contain SQL string interpolation. The reviewed secure authentication service still contains the same unsafe SQL interpolation. Do not mark the secure SQLi defense complete until this is fixed and tested. |
| 1.10 | OS command injection / RCE — Commix | **Safe simulation / partial:** vulnerable diagnostics displays a simulated command and fictional output; it does not execute the injected command. Secure diagnostics uses an argument list, input checks, and a timeout. Document the professor's RCE objective as a harmless simulation; do not create a reverse shell. |
| 1.11 | Stored XSS and session cookie exposure — XSStrike | **Partial:** vulnerable session cookies disable HttpOnly and Secure. Secure enables HttpOnly and SameSite=Lax, but Secure is environment-dependent and defaults to False. The secure announcement template still renders announcement content with the safe filter. Use only synthetic cookie values. |
| 1.12 | Directory traversal — DotDotPwn | **Implemented in source, testing pending:** vulnerable download joins a user-controlled path; secure download uses document IDs, safe_join, and ownership checks. Validate with synthetic files only. |
| 1.13 | Password hashing / dictionary attack — Hashcat | **Implemented in source, testing pending:** vulnerable version uses deliberately weak PBKDF2-SHA256 (one iteration, short salt); secure version uses Argon2id. Generate hashes only for synthetic accounts. |
| 1.14 | JWT tampering / privilege escalation — jwt_tool | **Partial:** vulnerable version uses a known fallback signing secret and trusts the role claim in /api/me. Secure configuration requires long secrets and the API reloads the role from the database. Strict issuer/audience validation and complete token tests still need review. |

### Important code-review findings

These issues should be addressed before the secure application is presented as fully hardened:

1. **SQL injection:** **academic_secure/services/auth_service.py** currently contains the same f-string SQL query construction as the vulnerable authentication service. Replace it with parameterized ORM queries or bound SQL parameters.
2. **Stored XSS:** **academic_secure/templates/announcements/detail.html** still applies Jinja's safe filter to **announcement.content**. Remove unsafe rendering unless a rigorously sanitized HTML requirement is deliberately implemented.
3. **Cookie transport:** **SESSION_COOKIE_SECURE** in the secure configuration defaults to **False**. Set it to **True** in the HTTPS deployment and verify the resulting cookie attributes.
4. **TLS identity:** the reported self-signed certificate does not identify the server IP in its SAN. Use a trusted lab CA and an IP SAN or a consistent DNS name.
5. **Deployment ports:** reconcile the Flask development entry points, Nginx listeners, Nginx upstream ports, and the reported Windows-hosted endpoints before changing deployment settings.

## Testing rules and safety

- Run tests only against the two project applications and the explicitly authorized lab host.
- Use synthetic users, passwords, session cookies, JWTs, documents, and academic records.
- Keep the vulnerable service isolated and never expose it to the public internet.
- Avoid destructive SQL operations, arbitrary file reads, persistence, real remote shells, and testing unrelated hosts.
- For command-execution and browser-permission missions, use harmless local demonstrations or simulations.
- Do not commit session cookies, private keys, passwords, JWT signing secrets, or personal data.
- Redact secrets and cookie values from terminal output, screenshots, logs, and the final report.

## Evidence standard

For each mission, record:

1. **Objective** — the weakness being tested.
2. **Source review** — the actual route, template, model, or configuration involved.
3. **Vulnerable test** — the authorized test and observed behavior.
4. **Impact** — what the result demonstrates, without overstating it.
5. **Secure test** — the equivalent test against the hardened instance.
6. **Mitigation** — the precise defensive code or configuration.
7. **Evidence** — sanitized request/response, output, screenshot, or test result.
8. **Oral explanation** — root cause, impact, and why the defense works.

Do not mark a mission complete because a header exists or a test returns an expected status code alone. Verify the underlying behavior too.

## Team and operating workflow

- **Team member A:** Arch Linux attacker/testing workstation.
- **Team member B:** Windows laptop hosting the applications.
- **Reported server IP:** 192.168.137.200.

When giving practical steps, keep attacker and server instructions separate:

- Arch Linux commands for the testing workstation.
- PowerShell commands for Windows configuration when needed.
- Explain what each command does and what result to expect.
- Use actual repository routes and parameter names; do not invent endpoints.
- Work in small, verifiable steps and diagnose failures before proposing workarounds.

## Current next steps

1. Reconcile the actual Windows deployment with the checked-in Nginx and Flask port configuration.
2. Fix the secure authentication SQL injection and unsafe announcement HTML rendering.
3. Resolve the lab TLS certificate identity and trust issue.
4. Run the 14 missions one at a time, collecting evidence for both versions.
5. Update the mission matrix only when the test and its defensive comparison have been verified.

## License

See [LICENSE](LICENSE).
