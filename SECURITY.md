# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| `main` (pre-release) | Yes |

Once versioned releases are available, only the latest minor release
within the current major version will receive security fixes.

## Reporting a Vulnerability

**Please do not report security vulnerabilities via public GitHub issues.**

Send a description of the vulnerability to the project maintainer.
You will receive an acknowledgement within 72 hours and a resolution
timeline within 7 days.

Please include:
- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept
- Any suggested fixes (optional but appreciated)

## Scope

The following are in scope:
- Authentication and session handling
- License validation bypass
- SQL injection or data exposure
- SSRF, XSS, or CSRF vulnerabilities
- Sensitive data exposure in logs or API responses

## Out of Scope

- Vulnerabilities in third-party dependencies (report upstream)
- Issues requiring physical access to the server
- Social engineering attacks

## Disclosure Policy

We follow coordinated disclosure. Please allow reasonable time
for a fix to be developed and released before publishing details.
