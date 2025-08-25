# Contributing to Oatie AI Reporting

Thank you for your interest in contributing to Oatie! This document provides guidelines and information for contributors.

## 🌟 Ways to Contribute

- **Bug Reports**: Report bugs via GitHub Issues
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests with bug fixes or new features
- **Documentation**: Improve documentation and examples
- **Testing**: Help improve test coverage and quality

## 🚀 Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/oatie-ai-reporting.git
   cd oatie-ai-reporting
   ```

2. **Set Up Development Environment**
   ```bash
   # Python backend
   python -m venv venv
   source venv/bin/activate
   pip install -e ".[dev]"
   
   # Node.js frontend
   npm install
   ```

3. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Workflow

1. **Make Changes**: Implement your feature or bug fix
2. **Test**: Ensure all tests pass and add new tests if needed
3. **Format**: Run code formatters and linters
4. **Document**: Update documentation as needed
5. **Commit**: Use conventional commit messages
6. **Push**: Push your branch to your fork
7. **Pull Request**: Create a pull request with detailed description

## 📝 Code Standards

### Python Backend

- **Formatting**: Use Black with 88-character line length
- **Linting**: Follow Pylint rules with our custom configuration
- **Type Hints**: Use comprehensive type hints and MyPy checking
- **Documentation**: Include docstrings for all public functions/classes
- **Testing**: Maintain >95% test coverage

```bash
# Format and check Python code
black backend/
isort backend/
pylint backend/oatie/
mypy backend/oatie/
pytest --cov=oatie
```

### TypeScript Frontend

- **Formatting**: Use Prettier with our configuration
- **Linting**: Follow ESLint rules with strict TypeScript
- **Type Safety**: Use strict TypeScript configuration
- **Accessibility**: Follow WCAG guidelines and use jsx-a11y
- **Testing**: Maintain >90% test coverage

```bash
# Format and check TypeScript code
npm run format
npm run lint
npm run type-check
npm run test:coverage
```

### Git Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test-related changes
- `chore`: Build process or auxiliary tool changes

**Examples:**
```
feat(api): add AI-powered report generation endpoint
fix(ui): resolve accessibility issues in report viewer
docs(readme): update installation instructions
test(backend): add unit tests for authentication service
```

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests**: Test individual functions/components
2. **Integration Tests**: Test API endpoints and service integration
3. **End-to-End Tests**: Test complete user workflows
4. **Security Tests**: Test for vulnerabilities and security issues

### Writing Tests

- **Descriptive Names**: Use clear, descriptive test names
- **Arrange-Act-Assert**: Follow AAA pattern for test structure
- **Mock External Dependencies**: Use mocking for external services
- **Test Edge Cases**: Include boundary conditions and error cases

### Running Tests

```bash
# Backend tests
pytest                           # All tests
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest --cov=oatie --cov-report=html  # With coverage

# Frontend tests
npm test                        # All tests
npm run test:coverage          # With coverage
npm run test:ui                # Interactive UI
```

## 🔒 Security Guidelines

### Security Best Practices

- **No Secrets in Code**: Never commit API keys, passwords, or secrets
- **Input Validation**: Validate all inputs on both client and server
- **Dependency Updates**: Keep dependencies updated and secure
- **Error Handling**: Don't expose sensitive information in errors
- **Authentication**: Use proper authentication and authorization

### Security Testing

- **SAST**: Use Bandit for static analysis security testing
- **Dependency Scanning**: Use Safety and npm audit for vulnerabilities
- **Manual Testing**: Perform manual security testing for critical features

## 📋 Pull Request Process

### Before Submitting

1. **Rebase**: Rebase your branch on the latest main branch
2. **Test**: Ensure all tests pass locally
3. **Format**: Run all formatters and linters
4. **Documentation**: Update relevant documentation
5. **Changelog**: Add entry to CHANGELOG.md if applicable

### Pull Request Template

When creating a pull request, include:

- **Description**: Clear description of changes and motivation
- **Type**: Bug fix, feature, documentation, etc.
- **Testing**: Description of testing performed
- **Screenshots**: For UI changes, include before/after screenshots
- **Breaking Changes**: List any breaking changes
- **Related Issues**: Reference related GitHub issues

### Review Process

1. **Automated Checks**: All CI/CD checks must pass
2. **Code Review**: At least one maintainer review required
3. **Testing**: Reviewers may request additional testing
4. **Documentation**: Ensure documentation is complete and accurate
5. **Approval**: Pull request approved by maintainer(s)

## 🏷️ Issue Guidelines

### Bug Reports

Include the following information:

- **Environment**: OS, Python version, Node.js version
- **Steps to Reproduce**: Clear steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Error Messages**: Include complete error messages and stack traces
- **Screenshots**: Include screenshots if applicable

### Feature Requests

Include the following information:

- **Use Case**: Describe the use case and motivation
- **Proposed Solution**: Describe your proposed solution
- **Alternatives**: Describe alternatives you've considered
- **Implementation**: Any thoughts on implementation approach

## 🎯 Areas for Contribution

### High Priority Areas

- **AI Integration**: Enhance AI-powered features
- **Oracle Integration**: Improve Oracle BI Publisher integration
- **Performance**: Optimize application performance
- **Security**: Enhance security features and testing
- **Accessibility**: Improve accessibility compliance

### Good First Issues

Look for issues labeled with:
- `good first issue`: Beginner-friendly issues
- `help wanted`: Issues where help is specifically requested
- `documentation`: Documentation improvements
- `testing`: Test-related improvements

## 📞 Getting Help

- **GitHub Discussions**: Ask questions and discuss ideas
- **GitHub Issues**: Report bugs and request features
- **Code Reviews**: Get feedback on your code changes
- **Email**: Contact maintainers directly if needed

## 🙏 Recognition

Contributors are recognized in:

- **CONTRIBUTORS.md**: List of all contributors
- **Release Notes**: Major contributions mentioned in releases
- **GitHub**: Contributor statistics and graphs
- **Special Thanks**: Outstanding contributions get special recognition

---

Thank you for contributing to Oatie AI Reporting! Your contributions help make this project better for everyone. 🎉