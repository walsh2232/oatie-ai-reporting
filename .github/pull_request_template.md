---
name: Pull Request
about: Submit changes for review
title: '[FEATURE/FIX/DOCS] Brief description'
labels: ''
assignees: ''
---

## 📋 Pull Request Checklist

- [ ] I have read the [Contributing Guidelines](CONTRIBUTING.md)
- [ ] My code follows the project's code style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have added documentation for my changes where appropriate

## 🎯 Description

Brief description of the changes and why they are needed.

Fixes #(issue_number)

## 🔄 Type of Change

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Maintenance/Refactoring
- [ ] 🧪 Test improvements
- [ ] 🔒 Security update

## 🧪 Testing

### Test Coverage
- [ ] Backend tests pass: `pytest --cov=app`
- [ ] Frontend tests pass: `npm test`
- [ ] Integration tests pass
- [ ] Manual testing completed

### Test Details
Describe the tests you ran to verify your changes:

1. **Unit Tests**: 
2. **Integration Tests**: 
3. **Manual Testing**: 

## 📊 Performance Impact

- [ ] No performance impact
- [ ] Performance improvement
- [ ] Potential performance regression (explain below)

**Performance Notes**: 

## 🔒 Security Considerations

- [ ] No security implications
- [ ] Security improvement
- [ ] Potential security impact (explain below)

**Security Notes**: 

## 📸 Screenshots (if applicable)

### Before
<!-- Add screenshot of the current state -->

### After
<!-- Add screenshot of the new state -->

## 🗂️ Database Changes

- [ ] No database changes
- [ ] Database schema changes (migration required)
- [ ] Data migration required

**Migration Details**: 

## 📝 Additional Context

Add any other context about the pull request here.

## 🔍 Review Focus Areas

Please pay special attention to:

- [ ] Code quality and maintainability
- [ ] Test coverage and edge cases
- [ ] Performance implications
- [ ] Security considerations
- [ ] Documentation accuracy

## 📋 Deployment Notes

Special considerations for deployment:

- [ ] No special deployment requirements
- [ ] Environment variables need updating
- [ ] Infrastructure changes required
- [ ] Manual steps required post-deployment

**Deployment Details**: 

---

## 🤖 GitHub Pro Features Used

- [ ] **GitHub Copilot**: Used for code generation/assistance
- [ ] **Advanced Security**: Dependabot/security alerts addressed
- [ ] **Actions**: CI/CD pipeline validated (3,000 minutes available)
- [ ] **Code Review**: Leveraging protected branch features

---

**Reviewers**: Please ensure all CI checks pass before approving. This PR will be automatically deployed to staging upon merge.
