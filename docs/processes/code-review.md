# Code Review Process

## Overview

This document outlines the code review process for the Oatie project, ensuring consistent quality, knowledge sharing, and maintainable code.

## Code Review Principles

### Quality Gates

All code must pass through the following quality gates:

1. **Automated Checks**: All CI/CD pipeline checks must pass
2. **Peer Review**: At least one approved review from a team member
3. **Test Coverage**: Maintain or improve test coverage (≥95%)
4. **Documentation**: Update relevant documentation
5. **Security Review**: Consider security implications

### Review Criteria

#### Code Quality
- [ ] Follows project coding standards and conventions
- [ ] Code is readable and well-structured
- [ ] Appropriate use of design patterns
- [ ] No code duplication without justification
- [ ] Proper error handling and logging

#### Functionality
- [ ] Code works as intended
- [ ] Edge cases are handled appropriately
- [ ] Performance considerations addressed
- [ ] No breaking changes without proper versioning

#### Testing
- [ ] Adequate test coverage for new/modified code
- [ ] Tests are meaningful and test the right things
- [ ] Tests are maintainable and not brittle
- [ ] Integration tests for API changes

#### Security
- [ ] No hardcoded secrets or sensitive data
- [ ] Input validation where appropriate
- [ ] Authentication/authorization properly implemented
- [ ] SQL injection and XSS prevention measures

#### Documentation
- [ ] Code is self-documenting or properly commented
- [ ] API documentation updated if applicable
- [ ] README and other docs updated as needed
- [ ] Breaking changes documented

## Review Process

### 1. Author Preparation

Before requesting review:

```bash
# Ensure your branch is up to date
git checkout main
git pull upstream main
git checkout your-feature-branch
git rebase main

# Run quality checks locally
npm run lint:fix
npm run test
npm run build

# Or for Python
black .
isort .
pylint src/
pytest --cov=src
```

### 2. Pull Request Creation

- Use the PR template
- Provide clear description and context
- Link related issues
- Add appropriate labels
- Request specific reviewers
- Include screenshots for UI changes

### 3. Review Assignment

#### Automatic Assignment
- Code owners are automatically requested for review
- Security-sensitive changes require security team review
- Architecture changes require architect review

#### Manual Assignment
- Author can request specific reviewers
- Consider expertise areas when choosing reviewers
- Distribute review load across team members

### 4. Review Execution

#### For Reviewers

**Time Expectations**:
- Initial review within 24 hours (business days)
- Follow-up reviews within 4 hours
- Large PRs (>400 lines): up to 48 hours

**Review Approach**:
1. **High-level review**: Understand the changes and approach
2. **Detailed review**: Line-by-line code examination
3. **Testing**: Pull and test changes locally if needed
4. **Documentation**: Verify docs are updated

**Providing Feedback**:
- Be specific and constructive
- Explain the "why" behind suggestions
- Distinguish between "must fix" and "nice to have"
- Offer solutions, not just problems
- Use code suggestions feature for specific fixes

**Review Categories**:
- **Approve**: Ready to merge
- **Request Changes**: Issues that must be addressed
- **Comment**: Feedback that doesn't block merge

#### For Authors

**Responding to Feedback**:
- Address all comments (even if just acknowledging)
- Ask for clarification if feedback is unclear
- Make requested changes in new commits (don't force push)
- Re-request review after making changes
- Thank reviewers for their time and feedback

### 5. Merge Process

#### Prerequisites for Merge
- [ ] All required reviews approved
- [ ] All CI checks passing
- [ ] No merge conflicts
- [ ] Branch is up to date with main
- [ ] All conversations resolved

#### Merge Methods
- **Squash and Merge**: Default for feature branches
- **Merge Commit**: For release branches
- **Rebase and Merge**: For hotfixes

```bash
# Squash merge example
git checkout main
git merge --squash feature/branch-name
git commit -m "feat: implement new feature"
git push origin main
```

## Review Guidelines by Change Type

### New Features

**Required Reviews**: 2 approvals
**Additional Checks**:
- [ ] Feature flag implementation (if applicable)
- [ ] Performance impact assessment
- [ ] Accessibility compliance
- [ ] Mobile responsiveness (if UI)
- [ ] API documentation updated
- [ ] User acceptance criteria met

### Bug Fixes

**Required Reviews**: 1 approval
**Additional Checks**:
- [ ] Root cause identified and addressed
- [ ] Test case added to prevent regression
- [ ] Related bugs checked for similar issues
- [ ] Hotfix process followed (if critical)

### Refactoring

**Required Reviews**: 1-2 approvals (depends on scope)
**Additional Checks**:
- [ ] Behavior unchanged (no regression)
- [ ] Performance impact neutral or positive
- [ ] Tests still pass and provide same coverage
- [ ] Migration plan for breaking changes

### Documentation

**Required Reviews**: 1 approval
**Additional Checks**:
- [ ] Technical accuracy verified
- [ ] Grammar and spelling checked
- [ ] Examples tested and working
- [ ] Screenshots up to date

### Infrastructure/DevOps

**Required Reviews**: DevOps team approval
**Additional Checks**:
- [ ] Security implications reviewed
- [ ] Backward compatibility maintained
- [ ] Rollback plan documented
- [ ] Monitoring and alerting updated

## Common Review Patterns

### Python Code Review

```python
# ❌ Avoid
def process_data(data):
    result = []
    for item in data:
        if item.status == "active":
            result.append(item.value * 2)
    return result

# ✅ Prefer
def process_active_data(data: List[DataItem]) -> List[float]:
    """Process active data items by doubling their values.
    
    Args:
        data: List of data items to process
        
    Returns:
        List of processed values for active items
    """
    return [item.value * 2 for item in data if item.status == "active"]
```

### TypeScript Code Review

```typescript
// ❌ Avoid
function updateUser(id: any, data: any): any {
  // Implementation
}

// ✅ Prefer
interface UpdateUserData {
  name?: string;
  email?: string;
  role?: UserRole;
}

function updateUser(id: string, data: UpdateUserData): Promise<User> {
  // Implementation with proper typing
}
```

## Review Metrics and Monitoring

### Key Metrics
- **Review Turnaround Time**: Target < 24 hours
- **Review Coverage**: 100% of PRs reviewed
- **Review Quality**: Defect escape rate < 5%
- **Review Distribution**: Balanced across team members

### Monitoring Tools
- GitHub PR analytics
- Code review dashboard
- Quality metrics tracking
- Team retrospectives

## Escalation Process

### When to Escalate
- Disagreement on technical approach
- Review taking too long (>48 hours)
- Reviewer unavailable
- Security concerns

### Escalation Path
1. **Team Lead**: Technical disagreements
2. **Architecture Team**: Design decisions
3. **Security Team**: Security concerns
4. **Engineering Manager**: Process issues

## Tools and Automation

### GitHub Features
- **Code Owners**: Automatic reviewer assignment
- **Draft PRs**: Work-in-progress reviews
- **Review Comments**: Threaded discussions
- **Suggestions**: Inline code fixes
- **Auto-merge**: Automatic merge when criteria met

### External Tools
- **SonarQube**: Code quality analysis
- **CodeClimate**: Maintainability scores
- **Snyk**: Security vulnerability scanning
- **Codecov**: Coverage reporting

## Best Practices

### For Everyone
- Keep PRs small and focused (< 400 lines)
- Write descriptive commit messages
- Include tests with code changes
- Update documentation
- Be respectful and constructive

### For Authors
- Self-review before requesting review
- Provide context and reasoning
- Test changes thoroughly
- Consider backwards compatibility
- Think about edge cases

### For Reviewers
- Review promptly
- Focus on important issues
- Provide actionable feedback
- Test changes when possible
- Share knowledge and best practices

## Templates and Checklists

### PR Review Checklist

```markdown
## Code Quality
- [ ] Follows coding standards
- [ ] No code smells or anti-patterns
- [ ] Appropriate error handling
- [ ] No hardcoded values

## Testing
- [ ] Tests included and passing
- [ ] Coverage maintained/improved
- [ ] Edge cases tested
- [ ] Integration tests for APIs

## Security
- [ ] No secrets in code
- [ ] Input validation implemented
- [ ] Authorization checks in place
- [ ] Security best practices followed

## Documentation
- [ ] Code comments where needed
- [ ] API docs updated
- [ ] README updated if needed
- [ ] Breaking changes documented
```

This process ensures high-quality code, knowledge sharing, and maintainable software while supporting efficient development workflows.