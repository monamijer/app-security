# Application Security Lab: Secure vs. Vulnerable Application

A Bachelor 2 application-security project developed by two students. The project is designed to demonstrate how common application vulnerabilities can be exploited in a deliberately vulnerable service, and how appropriate security controls reduce or prevent the same attacks in a hardened service.

> **Educational lab only.** The vulnerable service is intentionally insecure. Run both services only in an isolated local development environment, using test data. Do not expose the vulnerable service to the public internet or use these techniques against systems without explicit authorization.

## Project goals

The application will expose two comparable versions of the same functionality:

| Service | Purpose | Expected behavior |
| --- | --- | --- |
| **Insecure port** | Demonstrate common security weaknesses in a controlled target. | Selected attacks should succeed, with their impact observable and documented. |
| **Secure port** | Demonstrate how defensive coding and configuration mitigate those weaknesses. | The same attack attempts should be rejected or safely handled. |

The two services should provide equivalent features and use comparable test data. This makes the security controls—not differences in functionality—the main variable in the comparison.

## Learning objectives

- Identify common web-application vulnerabilities and understand their root causes.
- Demonstrate attacks against a deliberately vulnerable implementation in a controlled lab.
- Implement and explain defensive measures in the secure implementation.
- Compare the results using repeatable test cases and evidence.
- Communicate security findings, limitations, and recommendations.

## Planned architecture

The project will run two application instances:

- **Insecure instance:** contains explicitly documented, intentionally introduced vulnerabilities.
- **Secure instance:** implements the same use cases with appropriate validation, authorization, safe data handling, and secure configuration.

The ports, framework, database, and deployment method will be documented here once the implementation choices are confirmed.

## Vulnerability and defense matrix

The final list must match the features actually implemented. Candidate topics include:

| Topic | Insecure demonstration | Secure counterpart |
| --- | --- | --- |
| SQL injection | Unsafe construction of database queries | Parameterized queries / prepared statements |
| Cross-site scripting (XSS) | Rendering untrusted input without context-aware escaping | Context-aware output encoding and safe rendering |
| Broken authentication | Weak login or session handling in a test-only account flow | Password hashing, secure session handling, and appropriate authentication checks |
| Broken access control / IDOR | Trusting a user-supplied object identifier without checking ownership | Server-side authorization on every protected operation |
| Input validation | Accepting unexpected or malformed input | Server-side validation with safe failure behavior |
| Security misconfiguration | Deliberately weak lab configuration, where appropriate | Secure defaults, reduced information disclosure, and appropriate headers |

These are **candidate demonstrations, not claims that the repository currently implements them**. Only include a topic in the final report after the corresponding behavior and mitigation have been implemented and tested.

## Repository status

This repository is at the documentation/planning stage. The application framework, endpoints, ports, database, and attack scenarios still need to be specified and implemented.

## Getting started

Setup and run commands will be added after the technology stack and project structure are selected.

The intended workflow is:

1. Install the documented dependencies.
2. Configure the application using local development settings.
3. Start the insecure and secure instances on separate ports.
4. Run the same authorized test cases against both instances.
5. Record the outcome, evidence, and explanation for each test.

Do not use real credentials, personal information, or production data in this lab.

## Testing and demonstration

For every selected vulnerability, document:

1. **Objective:** what weakness is being tested.
2. **Insecure test:** the request or action used against the vulnerable instance.
3. **Observed result:** what happened and what impact it demonstrates.
4. **Secure test:** the equivalent attempt against the hardened instance.
5. **Mitigation:** the code or configuration change that prevents the issue.
6. **Evidence:** sanitized screenshots, requests/responses, logs, or test output.

The expected result is not simply that the secure port is harder to attack. Each security control should be explainable and supported by a repeatable test.

## Safety boundaries

- Keep the intentionally vulnerable service bound to localhost or an isolated lab network.
- Never deploy the vulnerable instance to a public server.
- Use only accounts and data created for this exercise.
- Test only the two project instances and only within the scope agreed by the project team and instructor.
- Do not include real secrets, passwords, tokens, or personal data in source control or screenshots.

## Team

Developed by two Bachelor 2 students. Add team member names and individual responsibilities when agreed.

## Decisions to finalize

Before implementation, confirm:

- Application language and framework.
- Whether the application is a web app, API, or both.
- The exact features shared by the two instances.
- The selected vulnerabilities and corresponding mitigations.
- Port numbers and whether both instances use the same database or isolated databases.
- How the application will be started and tested (local commands, Docker, or another method).
- Whether the instructor expects a particular report format or attack-tool set.

## License

Add the license required by the course or chosen by the project authors.
