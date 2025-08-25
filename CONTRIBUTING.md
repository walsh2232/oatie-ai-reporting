# Contributing to Oatie AI Reporting Platform

Thank you for your interest in contributing to Oatie! This guide will help you get started with developing, testing, and contributing to the Oracle-based AI reporting platform.

## Table of Contents

- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Oracle Integration](#oracle-integration)
- [GitHub Copilot Agent Coordination](#github-copilot-agent-coordination)
- [Code Review Process](#code-review-process)
- [Getting Help](#getting-help)

## Development Setup

### Prerequisites

- **Node.js**: Version 18.0 or higher
- **npm**: Version 8.0 or higher
- **Git**: Latest version
- **Oracle Database**: 19c or higher (for full testing)
- **Code Editor**: VS Code recommended with TypeScript and ESLint extensions

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/walsh2232/oatie-ai-reporting.git
   cd oatie-ai-reporting
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up pre-commit hooks** (if available)
   ```bash
   npm run prepare
   ```

4. **Configure Oracle connection** (optional for UI development)
   - Set up Oracle database instance
   - Configure connection parameters in the app
   - Ensure proper network access and credentials

5. **Start development server**
   ```bash
   npm run dev
   ```

6. **Verify setup**
   ```bash
   npm run lint
   npm run build
   ```

### Development Environment

- **Frontend**: React 19 + TypeScript + Vite
- **Styling**: Material-UI with Oracle Redwood Design System
- **State Management**: React Query + React Hook Form
- **Build Tool**: Vite
- **Package Manager**: npm

## Coding Standards

### TypeScript Standards

- **Strict mode enabled**: All TypeScript strict checks must pass
- **Type hints required**: Avoid `any` types, use proper type definitions
- **Interface naming**: Use PascalCase for interfaces (e.g., `UserData`, `OracleConnection`)
- **Enum naming**: Use PascalCase for enums with descriptive names

```typescript
// ✅ Good
interface OracleConnectionData {
  host: string;
  port: number;
  serviceName: string;
  username: string;
  password: string;
}

// ❌ Avoid
interface connectionData {
  host: any;
  port: any;
  // ... 
}
```

### React Standards

- **Functional components**: Use function components with hooks
- **Component naming**: PascalCase for component names
- **Props interfaces**: Define interfaces for all component props
- **Hook dependencies**: Always specify complete dependency arrays

```tsx
// ✅ Good
interface DashboardProps {
  userName: string;
  onLogout: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ userName, onLogout }) => {
  // Component implementation
};
```

### Oracle Redwood Design System

- **Theme consistency**: Use the provided `oracleRedwoodTheme`
- **Color palette**: Use theme colors instead of hardcoded values
- **Typography**: Follow Oracle Sans typography hierarchy
- **Spacing**: Use Material-UI spacing units (theme.spacing())

```tsx
// ✅ Good
<Box sx={{ 
  padding: theme.spacing(2), 
  backgroundColor: theme.palette.primary.main 
}}>

// ❌ Avoid
<Box sx={{ 
  padding: '16px', 
  backgroundColor: '#da2b2b' 
}}>
```

### File Structure

```
src/
├── components/          # Reusable UI components
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── theme/              # Oracle Redwood theme configuration
├── types/              # TypeScript type definitions
├── services/           # API and Oracle integration services
└── __tests__/          # Test files
```

## Pull Request Process

### Branch Strategy

- **Main branch**: `main` - Production-ready code
- **Feature branches**: `feature/description` - New features
- **Bug fixes**: `bugfix/description` - Bug fixes
- **Documentation**: `docs/description` - Documentation updates

### Commit Standards

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

**Examples:**
```bash
feat(dashboard): add Oracle performance metrics visualization
fix(auth): resolve login timeout issue with Oracle connection
docs(api): update Oracle integration endpoints documentation
```

### Pull Request Steps

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes following coding standards**
   - Write code with proper TypeScript types
   - Follow Oracle Redwood design patterns
   - Add appropriate error handling

3. **Test your changes**
   ```bash
   npm run lint
   npm run build
   npm run test  # when available
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push branch and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Fill out PR template completely**
   - Describe changes and motivation
   - List testing performed
   - Add screenshots for UI changes
   - Reference related issues

## Testing Guidelines

### Test Structure (Future Implementation)

When testing framework is added, follow these guidelines:

- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test Oracle database integration
- **E2E Tests**: Test complete user workflows
- **Performance Tests**: Test Oracle query performance

### Manual Testing

For now, perform thorough manual testing:

1. **UI Testing**
   - Test all user interactions
   - Verify Oracle Redwood design compliance
   - Test responsive design on different screen sizes

2. **Oracle Integration Testing**
   - Test database connections
   - Verify query performance
   - Test error handling for connection failures

3. **Cross-browser Testing**
   - Chrome (primary)
   - Firefox
   - Safari
   - Edge

## Oracle Integration

### Database Considerations

- **Connection Pooling**: Use efficient connection management
- **Query Optimization**: Write performant Oracle SQL queries
- **Error Handling**: Implement proper Oracle-specific error handling
- **Security**: Follow Oracle security best practices

### Performance Guidelines

- **Lazy Loading**: Implement for large datasets
- **Pagination**: Use Oracle ROWNUM or OFFSET/FETCH for large results
- **Caching**: Cache frequently accessed Oracle data
- **Connection Management**: Properly close connections

## GitHub Copilot Agent Coordination

### Agent Assignment

When working with GitHub Copilot agents:

1. **Clear Task Boundaries**
   - Assign specific files or modules to agents
   - Avoid overlapping responsibilities
   - Use PR comments to coordinate changes

2. **Progress Tracking**
   - Regular status updates in PR comments
   - Use issue milestones for larger features
   - Daily sync through issue comments

3. **Quality Control**
   - All agent changes require human review
   - Follow same code review standards
   - Test agent-generated code thoroughly

### Resource Management

- **API Rate Limits**: Be mindful of GitHub API usage
- **Concurrent Agents**: Coordinate to avoid conflicts
- **Documentation**: Keep agent coordination docs updated

## Code Review Process

### Review Requirements

- **Minimum Reviewers**: 1 human reviewer required
- **Automated Checks**: All CI checks must pass
- **Review Checklist**: Use the provided review template

### Review Guidelines

**As a Reviewer:**
- Check code quality and standards compliance
- Verify Oracle integration patterns
- Test changes locally when possible
- Provide constructive feedback
- Approve only when confident in changes

**As a Author:**
- Respond to feedback promptly
- Make requested changes
- Re-request review after changes
- Ensure CI checks pass

### Common Review Points

- **TypeScript Types**: No `any` types without justification
- **Error Handling**: Proper error boundaries and user feedback
- **Performance**: Efficient Oracle queries and React rendering
- **Security**: No hardcoded credentials or vulnerabilities
- **Accessibility**: ARIA labels and keyboard navigation
- **Oracle Compliance**: Follows Redwood design patterns

## Getting Help

### Resources

- **Documentation**: Check README and in-code comments
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Oracle Docs**: Reference Oracle database documentation

### Communication

- **GitHub Issues**: For bugs and feature requests
- **Pull Request Comments**: For code-specific discussions
- **Commit Messages**: For documenting changes

### Escalation

For complex issues:
1. Create detailed GitHub issue
2. Tag relevant maintainers
3. Provide reproduction steps
4. Include environment details

---

## Development Workflow Summary

1. **Setup**: Clone repo, install dependencies, configure environment
2. **Develop**: Create feature branch, write code following standards
3. **Test**: Run linting, builds, and manual testing
4. **Submit**: Create PR with complete description and testing details
5. **Review**: Address feedback, ensure CI passes
6. **Merge**: Maintainer merges after approval

Thank you for contributing to Oatie AI Reporting Platform! 🚀