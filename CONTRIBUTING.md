# Contributing to Oatie AI Reporting

Welcome to the Oatie AI Reporting project! This document provides guidelines for contributing to our Oracle BI reporting application built with React, TypeScript, and the Oracle Redwood design system.

## Table of Contents

- [Development Workflow](#development-workflow)
- [Branching Strategy](#branching-strategy)
- [Commit Conventions](#commit-conventions)
- [Code Review Process](#code-review-process)
- [Getting Started](#getting-started)
- [Common Tasks](#common-tasks)

## Development Workflow

Our development workflow follows a structured approach to ensure code quality and maintainability:

### 1. Issue Creation
- Create detailed issues for bugs, features, or improvements
- Use appropriate labels: `bug`, `feature`, `enhancement`, `documentation`
- Include Oracle BI context when relevant
- Reference related Oracle components or functionality

### 2. Development Process
1. **Assign Issue**: Self-assign or get assigned to an issue
2. **Create Branch**: Create a feature branch from `main`
3. **Develop**: Implement changes following our coding standards
4. **Test**: Ensure all tests pass and add new tests as needed
5. **Lint**: Fix all linting errors before submitting
6. **Submit PR**: Create a pull request with detailed description
7. **Review**: Address feedback from code review
8. **Merge**: Merge after approval and passing CI/CD

## Branching Strategy

We use a **GitHub Flow** strategy with the following conventions:

### Branch Types

- **`main`**: Production-ready code, always deployable
- **`feature/*`**: New features (e.g., `feature/oracle-dashboard-enhancement`)
- **`bugfix/*`**: Bug fixes (e.g., `bugfix/connection-dialog-validation`)
- **`hotfix/*`**: Critical production fixes
- **`docs/*`**: Documentation updates (e.g., `docs/api-documentation`)

### Branch Naming Convention

```
<type>/<short-description>
```

Examples:
- `feature/oracle-redwood-theming`
- `bugfix/parallel-processor-memory-leak`
- `docs/contributing-guidelines`
- `hotfix/security-vulnerability`

### Branch Lifecycle

1. **Create**: Branch from `main` for new work
2. **Develop**: Make commits following our commit conventions
3. **Push**: Push branch to remote repository
4. **PR**: Create pull request when ready for review
5. **Review**: Go through code review process
6. **Merge**: Merge to `main` after approval
7. **Cleanup**: Delete feature branch after merge

## Commit Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to our CI configuration files and scripts

### Examples

```bash
# Feature commits
feat(dashboard): add Oracle BI performance metrics chart
feat(auth): implement Oracle SSO integration

# Bug fix commits
fix(connection): resolve timeout issue in Oracle connection dialog
fix(theme): correct Oracle Redwood color inconsistencies

# Documentation commits
docs(api): update Oracle parallel processor documentation
docs(setup): add Oracle database configuration guide

# Refactoring commits
refactor(utils): optimize Oracle query parallel processing
refactor(components): extract reusable Oracle UI components
```

### Scope Guidelines

Common scopes in our project:
- `dashboard`: Dashboard-related changes
- `auth`: Authentication and authorization
- `theme`: Oracle Redwood theming
- `connection`: Oracle database connections
- `utils`: Utility functions and helpers
- `components`: React components
- `api`: API-related changes

## Code Review Process

### Review Checklist

#### Functionality
- [ ] Code solves the stated problem
- [ ] Oracle BI integration works correctly
- [ ] No breaking changes without proper migration
- [ ] Performance implications considered

#### Code Quality
- [ ] Follows TypeScript best practices
- [ ] Adheres to Oracle Redwood design patterns
- [ ] No TypeScript `any` types without justification
- [ ] Proper error handling implemented
- [ ] Memory leaks prevented (especially in parallel processing)

#### Testing
- [ ] Unit tests added/updated for new functionality
- [ ] Integration tests cover Oracle connections
- [ ] Manual testing performed
- [ ] Edge cases considered

#### Documentation
- [ ] Code is self-documenting with clear variable names
- [ ] Complex logic includes comments
- [ ] JSDoc comments for public APIs
- [ ] README updated if needed

### Review Timeline

- **Initial Review**: Within 24 hours of PR creation
- **Re-review**: Within 8 hours of addressing feedback
- **Approval**: Required from at least one team member
- **Merge**: After approval and passing CI/CD checks

### Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Self Review**: Author reviews their own PR first
3. **Peer Review**: Team members review code and provide feedback
4. **Address Feedback**: Author makes requested changes
5. **Final Approval**: Reviewer approves changes
6. **Merge**: PR is merged to main branch

## Getting Started

See our [Onboarding Guide](./ONBOARDING.md) for detailed setup instructions.

## Common Tasks

### Adding a New Oracle Component

1. Create component in `src/components/`
2. Follow Oracle Redwood design patterns
3. Use TypeScript interfaces for props
4. Add to theme exports if reusable
5. Write unit tests
6. Update Storybook documentation (if applicable)

### Updating Oracle Theme

1. Modify `src/theme/oracleRedwoodTheme.ts`
2. Test with existing components
3. Update CSS variables in `src/index.css`
4. Document changes in theme documentation

### Adding New Oracle BI Features

1. Plan parallel processing requirements
2. Update `src/utils/parallelProcessor.ts` if needed
3. Implement React components with proper TypeScript types
4. Add Oracle connection handling
5. Write comprehensive tests
6. Update API documentation

### Working with Oracle Connections

1. Use existing `OracleConnectionDialog` patterns
2. Implement proper validation with Yup schemas
3. Handle connection errors gracefully
4. Test with various Oracle configurations
5. Document connection requirements

## Questions?

- Check our [Coding Standards](./CODING_STANDARDS.md)
- Review the [Onboarding Guide](./ONBOARDING.md)
- Create an issue for questions or clarifications