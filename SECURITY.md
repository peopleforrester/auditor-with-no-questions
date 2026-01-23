# Security Policy

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in this project, please report it responsibly.

### How to Report

1. **Do NOT** create a public GitHub issue for security vulnerabilities
2. Email the maintainer directly with details of the vulnerability
3. Include steps to reproduce the issue if possible
4. Allow reasonable time for a response before any public disclosure

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution Target**: Depends on severity

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Security Best Practices for Demo Code

The code in this repository is intended for educational and demonstration purposes at KubeCon Europe 2026. When adapting this code for production use:

1. **Never commit secrets** - Use secret management solutions
2. **Review RBAC policies** - Apply principle of least privilege
3. **Validate inputs** - All user inputs should be validated
4. **Keep dependencies updated** - Regularly update to patched versions
5. **Use network policies** - Restrict pod-to-pod communication as needed

## Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who report valid vulnerabilities (with their permission).
