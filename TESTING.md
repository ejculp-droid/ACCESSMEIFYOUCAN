# Testing Guide

## Overview

This guide covers testing strategies for the ACCESSMEIFYOUCAN platform.

## Testing Structure

```
tests/
├── unit/              # Unit tests for individual functions
├── integration/       # Integration tests for API endpoints
└── e2e/              # End-to-end tests (future)
```

## Backend Testing

### Unit Tests (Python)

#### Setup

```bash
cd backend
pip install pytest pytest-mock boto3 moto
```

#### Test File Structure

Create `tests/unit/test_auth.py`:

```python
import pytest
import json
from unittest.mock import Mock, patch
from src.auth.handler import lambda_handler, handle_register, handle_login

@pytest.fixture
def cognito_client_mock():
    with patch('src.auth.handler.cognito_client') as mock:
        yield mock

def test_register_success(cognito_client_mock):
    """Test successful user registration"""
    cognito_client_mock.sign_up.return_value = {
        'UserSub': 'test-user-id'
    }
    
    event = {
        'path': '/auth/register',
        'body': json.dumps({
            'email': 'test@example.com',
            'password': 'Test123!'
        })
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['message'] == 'User registered successfully'
    assert body['userId'] == 'test-user-id'

def test_register_missing_email():
    """Test registration with missing email"""
    event = {
        'path': '/auth/register',
        'body': json.dumps({
            'password': 'Test123!'
        })
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'Email and password required' in body['error']

def test_login_success(cognito_client_mock):
    """Test successful login"""
    cognito_client_mock.initiate_auth.return_value = {
        'AuthenticationResult': {
            'AccessToken': 'mock-access-token',
            'IdToken': 'mock-id-token',
            'RefreshToken': 'mock-refresh-token',
            'ExpiresIn': 3600
        }
    }
    
    cognito_client_mock.get_user.return_value = {
        'UserAttributes': [
            {'Name': 'custom:membershipTier', 'Value': 'Free'}
        ]
    }
    
    event = {
        'path': '/auth/login',
        'body': json.dumps({
            'email': 'test@example.com',
            'password': 'Test123!'
        })
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'accessToken' in body
    assert body['membershipTier'] == 'Free'
```

#### Running Unit Tests

```bash
cd backend
pytest tests/unit/ -v
```

### Integration Tests

Create `tests/integration/test_api.py`:

```python
import pytest
import boto3
import requests
import json
from moto import mock_dynamodb, mock_cognitoidp

@pytest.fixture
def api_base_url():
    """Get API base URL from environment or config"""
    return "https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/prod"

def test_register_and_login_flow(api_base_url):
    """Test complete registration and login flow"""
    # Register
    register_response = requests.post(
        f"{api_base_url}/auth/register",
        json={
            "email": f"test-{uuid.uuid4()}@example.com",
            "password": "Test123!@#"
        }
    )
    assert register_response.status_code == 201
    
    # Login
    login_response = requests.post(
        f"{api_base_url}/auth/login",
        json={
            "email": register_data['email'],
            "password": "Test123!@#"
        }
    )
    assert login_response.status_code == 200
    assert 'accessToken' in login_response.json()

def test_get_services_authenticated(api_base_url, access_token):
    """Test getting services with authentication"""
    response = requests.get(
        f"{api_base_url}/services",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert 'services' in data
    assert len(data['services']) == 4

def test_request_service_flow(api_base_url, access_token):
    """Test service request flow"""
    # Request service
    response = requests.post(
        f"{api_base_url}/services/request",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "category": "consulting",
            "requestData": {
                "prompt": "Test prompt for consulting service"
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'accepted'
    assert 'requestId' in data
```

#### Running Integration Tests

```bash
cd backend
# Set environment variables first
export API_BASE_URL=https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/prod
pytest tests/integration/ -v
```

## Frontend Testing

### Setup

```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

### Component Tests

Create `frontend/src/components/__tests__/Login.test.js`:

```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Login from '../Login';
import authService from '../../services/authService';

jest.mock('../../services/authService');

describe('Login Component', () => {
  test('renders login form', () => {
    render(<Login onLoginSuccess={() => {}} />);
    
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByText('Login')).toBeInTheDocument();
  });

  test('handles successful login', async () => {
    const mockOnLoginSuccess = jest.fn();
    authService.login.mockResolvedValue({ accessToken: 'mock-token' });
    
    render(<Login onLoginSuccess={mockOnLoginSuccess} />);
    
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'Test123!' }
    });
    fireEvent.click(screen.getByText('Login'));
    
    await waitFor(() => {
      expect(mockOnLoginSuccess).toHaveBeenCalled();
    });
  });

  test('displays error on failed login', async () => {
    authService.login.mockRejectedValue(new Error('Invalid credentials'));
    
    render(<Login onLoginSuccess={() => {}} />);
    
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'wrong' }
    });
    fireEvent.click(screen.getByText('Login'));
    
    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });
});
```

Create `frontend/src/services/__tests__/authService.test.js`:

```javascript
import authService from '../authService';
import axios from 'axios';

jest.mock('axios');

describe('AuthService', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  test('login stores tokens in localStorage', async () => {
    const mockResponse = {
      data: {
        accessToken: 'access-token',
        idToken: 'id-token',
        refreshToken: 'refresh-token',
        membershipTier: 'Free'
      }
    };
    axios.post.mockResolvedValue(mockResponse);
    
    await authService.login('test@example.com', 'Test123!');
    
    expect(localStorage.getItem('accessToken')).toBe('access-token');
    expect(localStorage.getItem('idToken')).toBe('id-token');
    expect(localStorage.getItem('refreshToken')).toBe('refresh-token');
  });

  test('logout clears localStorage', () => {
    localStorage.setItem('accessToken', 'token');
    localStorage.setItem('user', JSON.stringify({ email: 'test@example.com' }));
    
    authService.logout();
    
    expect(localStorage.getItem('accessToken')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  test('isAuthenticated returns true when token exists', () => {
    localStorage.setItem('accessToken', 'token');
    authService.token = 'token';
    
    expect(authService.isAuthenticated()).toBe(true);
  });
});
```

#### Running Frontend Tests

```bash
cd frontend
npm test
```

## Manual Testing

### Test Scenarios

#### 1. User Registration
- [ ] Register with valid email and password
- [ ] Verify Free tier is assigned
- [ ] Attempt duplicate registration (should fail)
- [ ] Register with weak password (should fail)

#### 2. User Login
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (should fail)
- [ ] Verify token is stored
- [ ] Verify user info is displayed

#### 3. Service Selection
- [ ] View available services
- [ ] Verify Free tier sees only Consulting & Technical
- [ ] Select a service
- [ ] Submit a request
- [ ] Verify request is processed

#### 4. Subscription Management
- [ ] View current subscription
- [ ] Upgrade from Free to Pro
- [ ] Verify new services are available
- [ ] Upgrade to Enterprise
- [ ] Verify all services available

#### 5. Governance Rules
- [ ] Exceed rate limit (should be throttled)
- [ ] Request unavailable service (should fail)
- [ ] Submit prohibited content (should be rejected)

### Load Testing

Use Apache Bench or Artillery:

```bash
# Install Artillery
npm install -g artillery

# Create test script
cat > load-test.yml << EOF
config:
  target: 'https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/prod'
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - flow:
      - post:
          url: "/auth/login"
          json:
            email: "test@example.com"
            password: "Test123!"
EOF

# Run load test
artillery run load-test.yml
```

## Test Data Management

### Setup Test Users

Create script `scripts/setup-test-data.py`:

```python
import boto3

cognito = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')

def create_test_users():
    users = [
        {'email': 'free@test.com', 'tier': 'Free'},
        {'email': 'pro@test.com', 'tier': 'Pro'},
        {'email': 'enterprise@test.com', 'tier': 'Enterprise'}
    ]
    
    for user in users:
        # Create user in Cognito
        # Create subscription in DynamoDB
        pass

if __name__ == '__main__':
    create_test_users()
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-mock
          pytest tests/unit/
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: |
          cd frontend
          npm install
          npm test -- --coverage
```

## Test Coverage Goals

- **Unit Tests**: > 80% coverage
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user flows

## Debugging Tests

### Backend Debugging

```python
# Add to test
import pdb; pdb.set_trace()
```

### Frontend Debugging

```javascript
// Add to test
screen.debug()  // Print DOM
console.log(screen.getByText('Login'))  // Find element
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Services**: Don't call real APIs in tests
3. **Clear Test Names**: Describe what's being tested
4. **Arrange-Act-Assert**: Structure tests clearly
5. **Test Edge Cases**: Not just happy path
6. **Clean Up**: Reset state after each test

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Pytest Documentation](https://docs.pytest.org/)
- [AWS Moto](https://github.com/spulec/moto) for mocking AWS services
