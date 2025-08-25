# Security Policy

## Supported Versions

We currently support the following versions of Oatie with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| 0.9.x   | :x:                |
| < 0.9   | :x:                |

## Reporting a Vulnerability

We take the security of Oatie seriously. If you discover a security vulnerability, please follow these steps:

### 🔒 For Security Vulnerabilities

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please:

1. **Report privately** by emailing security@oatie.ai
2. **Include detailed information**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)

### 📧 What to Include

- **Vulnerability Type**: (e.g., SQL injection, XSS, authentication bypass)
- **Component Affected**: (frontend, backend, database, infrastructure)
- **Attack Vector**: How the vulnerability can be exploited
- **Impact Assessment**: What could an attacker accomplish
- **Proof of Concept**: Steps to reproduce (if safe to do so)
- **Suggested Mitigation**: Any ideas for fixes

### ⏱️ Response Timeline

- **Acknowledgment**: Within 24 hours
- **Initial Assessment**: Within 72 hours
- **Status Update**: Weekly until resolved
- **Resolution**: Depends on severity (see below)

### 🚨 Severity Levels

| Severity | Response Time | Examples |
|----------|---------------|----------|
| **Critical** | 24-48 hours | Remote code execution, authentication bypass |
| **High** | 3-7 days | SQL injection, XSS, privilege escalation |
| **Medium** | 2-4 weeks | Information disclosure, CSRF |
| **Low** | 1-3 months | Rate limiting issues, minor information leaks |

### 🛡️ Security Measures in Place

#### Backend Security
- **Input Validation**: Comprehensive Pydantic validation
- **SQL Injection Prevention**: Parameterized queries with SQLAlchemy
- **Authentication**: JWT-based with secure token handling
- **Rate Limiting**: API endpoint protection
- **Dependency Scanning**: Automated vulnerability checks

#### Frontend Security
- **XSS Prevention**: Content Security Policy (CSP)
- **Authentication**: Secure token storage and handling
- **HTTPS**: Enforced secure connections
- **Input Sanitization**: Client-side validation
- **Dependency Scanning**: npm audit integration

#### Infrastructure Security
- **Container Security**: Multi-stage Docker builds
- **Secrets Management**: Environment variable protection
- **Network Security**: Proper port configuration
- **CI/CD Security**: Secure pipeline configuration

### 🔄 Security Update Process

1. **Vulnerability Assessment**: Evaluate severity and impact
2. **Fix Development**: Develop and test security patch
3. **Security Review**: Internal security team review
4. **Release Preparation**: Prepare security advisory
5. **Coordinated Disclosure**: Release fix and advisory
6. **Communication**: Notify users through multiple channels

### 📋 Security Checklist for Contributors

When contributing to Oatie, please ensure:

- [ ] **Input Validation**: All user inputs are properly validated
- [ ] **Authentication**: Proper access controls are in place
- [ ] **Error Handling**: No sensitive information in error messages
- [ ] **Logging**: No sensitive data logged
- [ ] **Dependencies**: No known vulnerable dependencies
- [ ] **Tests**: Security test cases included

### 🔍 Automated Security Scanning

We use several automated tools:

- **Dependabot**: Automated dependency updates
- **Trivy**: Container vulnerability scanning
- **Safety**: Python dependency vulnerability scanning
- **npm audit**: Node.js dependency vulnerability scanning
- **CodeQL**: Static code analysis (when available)

### 📞 Contact Information

- **Security Team**: security@oatie.ai
- **General Contact**: contact@oatie.ai
- **GitHub Issues**: For non-security bugs only

### 🏆 Recognition

We appreciate security researchers who help us maintain the security of Oatie. While we don't currently offer a bug bounty program, we will:

- Acknowledge your contribution in our security advisories
- Credit you in our release notes (if desired)
- Provide a reference letter for your responsible disclosure

### 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

---

**Last Updated**: January 2025
**Policy Version**: 1.0
