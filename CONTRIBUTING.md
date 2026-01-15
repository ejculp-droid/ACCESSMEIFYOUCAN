# Contributing to ACCESSMEIFYOUCAN

Thank you for your interest in contributing to ACCESSMEIFYOUCAN! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Pull Request Process](#pull-request-process)
7. [Issue Reporting](#issue-reporting)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## Getting Started

### Prerequisites

Before you begin, ensure you have:
- AWS Account with appropriate permissions
- AWS CLI configured
- Node.js 16+ and npm
- Python 3.11+
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/YOUR_USERNAME/ACCESSMEIFYOUCAN.git
cd ACCESSMEIFYOUCAN
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/ejculp-droid/ACCESSMEIFYOUCAN.git
```

### Development Setup

1. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
npm install
```

2. Install frontend dependencies:
```bash
cd ../frontend
npm install
```

3. Copy environment files:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Production hotfixes

### Creating a Branch

```bash
git checkout -b feature/your-feature-name
```

### Keeping Your Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

## Coding Standards

### Python Style Guide

Follow PEP 8 guidelines:

```python
# Good
def calculate_total(items, tax_rate=0.1):
    """
    Calculate total price including tax.
    
    Args:
        items: List of items with prices
        tax_rate: Tax rate as decimal (default: 0.1)
    
    Returns:
        Total price including tax
    """
    subtotal = sum(item['price'] for item in items)
    return subtotal * (1 + tax_rate)

# Bad
def calc(i,t=0.1):
    return sum([x['price'] for x in i])*(1+t)
```

**Key Points**:
- Use meaningful variable names
- Add docstrings to all functions
- Maximum line length: 100 characters
- Use type hints where appropriate

### JavaScript/React Style Guide

Follow Airbnb JavaScript Style Guide:

```javascript
// Good
const calculateTotal = (items, taxRate = 0.1) => {
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  return subtotal * (1 + taxRate);
};

// Bad
function calc(i,t) {
  return i.reduce((s,x)=>s+x.price,0)*(1+(t||0.1))
}
```

**Key Points**:
- Use arrow functions for callbacks
- Use destructuring where appropriate
- Prefer const/let over var
- Use meaningful component and variable names

### AWS Lambda Best Practices

```python
# Good - Single responsibility
def lambda_handler(event, context):
    """Handle authentication requests"""
    try:
        body = json.loads(event.get('body', '{}'))
        return process_auth_request(body)
    except Exception as e:
        return error_response(str(e))

# Bad - Too much logic in handler
def lambda_handler(event, context):
    # 100+ lines of logic here
```

**Key Points**:
- Keep handlers thin, move logic to separate functions
- Always handle exceptions
- Use environment variables for configuration
- Minimize cold start impact

## Testing Guidelines

### Writing Tests

Every new feature or bug fix should include tests.

#### Backend Tests

```python
# tests/unit/test_new_feature.py
import pytest
from src.feature import new_function

def test_new_function_success():
    """Test successful execution of new function"""
    result = new_function(valid_input)
    assert result == expected_output

def test_new_function_invalid_input():
    """Test new function handles invalid input"""
    with pytest.raises(ValueError):
        new_function(invalid_input)
```

#### Frontend Tests

```javascript
// components/__tests__/NewComponent.test.js
import { render, screen } from '@testing-library/react';
import NewComponent from '../NewComponent';

describe('NewComponent', () => {
  test('renders correctly', () => {
    render(<NewComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

### Running Tests

```bash
# Backend
cd backend
pytest tests/

# Frontend
cd frontend
npm test
```

### Test Coverage

- Aim for > 80% code coverage
- All public APIs must have tests
- Critical paths must have integration tests

## Pull Request Process

### Before Submitting

1. **Update from main**:
```bash
git fetch upstream
git rebase upstream/main
```

2. **Run tests**:
```bash
# Backend
cd backend && pytest tests/

# Frontend
cd frontend && npm test
```

3. **Check code style**:
```bash
# Python
black backend/src/
pylint backend/src/

# JavaScript
cd frontend && npm run lint
```

4. **Update documentation** if needed

### Submitting a Pull Request

1. Push to your fork:
```bash
git push origin feature/your-feature-name
```

2. Create Pull Request on GitHub

3. Fill out the PR template:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe tests performed

## Checklist
- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### PR Review Process

1. Automated checks must pass
2. At least one maintainer approval required
3. Address review feedback
4. Squash commits if requested
5. Maintainer will merge

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g., macOS]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]

**Additional context**
Any other relevant information
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution**
How you'd like this to work

**Alternatives considered**
Other solutions you've thought about

**Additional context**
Any other relevant information
```

## Architecture Decisions

For significant changes:

1. Open an issue for discussion
2. Create RFC (Request for Comments) document
3. Get feedback from maintainers
4. Proceed with implementation after approval

## Documentation

### Code Comments

```python
# Good - Explain WHY
# Using exponential backoff to handle API rate limits
for attempt in range(max_retries):
    try:
        return make_api_call()
    except RateLimitError:
        time.sleep(2 ** attempt)

# Bad - Explain WHAT (code already shows this)
# Loop 3 times
for i in range(3):
    do_something()
```

### API Documentation

Update API.md when changing endpoints:

```markdown
#### New Endpoint

**POST** `/new/endpoint`

Description of what it does

**Request:**
```json
{
  "field": "value"
}
```

**Response:**
```json
{
  "result": "success"
}
```
```

## Community

- **Questions**: Open a GitHub Discussion
- **Chat**: [Discord/Slack link if available]
- **Email**: [contact email if available]

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Getting Help

If you need help:
1. Check existing documentation
2. Search existing issues
3. Ask in GitHub Discussions
4. Contact maintainers

Thank you for contributing to ACCESSMEIFYOUCAN! 🎉
