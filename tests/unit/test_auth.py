"""
Unit tests for authentication handler
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError


# Mock the environment variables before importing the handler
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv('USER_POOL_ID', 'test-pool-id')
    monkeypatch.setenv('USER_POOL_CLIENT_ID', 'test-client-id')


@pytest.fixture
def mock_cognito_client():
    """Mock Cognito client"""
    with patch('backend.src.auth.handler.cognito_client') as mock:
        yield mock


def test_handle_register_success(mock_cognito_client):
    """Test successful user registration"""
    from backend.src.auth.handler import handle_register
    
    mock_cognito_client.sign_up.return_value = {
        'UserSub': 'test-user-123'
    }
    
    body = {
        'email': 'newuser@example.com',
        'password': 'SecurePass123!'
    }
    
    response = handle_register(body)
    
    assert response['statusCode'] == 201
    body_data = json.loads(response['body'])
    assert body_data['message'] == 'User registered successfully'
    assert body_data['userId'] == 'test-user-123'
    assert body_data['membershipTier'] == 'Free'


def test_handle_register_missing_email():
    """Test registration with missing email"""
    from backend.src.auth.handler import handle_register
    
    body = {'password': 'SecurePass123!'}
    
    response = handle_register(body)
    
    assert response['statusCode'] == 400
    body_data = json.loads(response['body'])
    assert 'Email and password required' in body_data['error']


def test_handle_register_duplicate_user(mock_cognito_client):
    """Test registration with existing user"""
    from backend.src.auth.handler import handle_register
    
    error = ClientError(
        {'Error': {'Code': 'UsernameExistsException', 'Message': 'User exists'}},
        'SignUp'
    )
    mock_cognito_client.sign_up.side_effect = error
    
    body = {
        'email': 'existing@example.com',
        'password': 'SecurePass123!'
    }
    
    response = handle_register(body)
    
    assert response['statusCode'] == 409
    body_data = json.loads(response['body'])
    assert 'already exists' in body_data['error']


def test_handle_login_success(mock_cognito_client):
    """Test successful login"""
    from backend.src.auth.handler import handle_login
    
    mock_cognito_client.initiate_auth.return_value = {
        'AuthenticationResult': {
            'AccessToken': 'mock-access-token',
            'IdToken': 'mock-id-token',
            'RefreshToken': 'mock-refresh-token',
            'ExpiresIn': 3600
        }
    }
    
    mock_cognito_client.get_user.return_value = {
        'UserAttributes': [
            {'Name': 'email', 'Value': 'user@example.com'},
            {'Name': 'custom:membershipTier', 'Value': 'Pro'}
        ]
    }
    
    body = {
        'email': 'user@example.com',
        'password': 'SecurePass123!'
    }
    
    response = handle_login(body)
    
    assert response['statusCode'] == 200
    body_data = json.loads(response['body'])
    assert 'accessToken' in body_data
    assert body_data['membershipTier'] == 'Pro'


def test_handle_login_invalid_credentials(mock_cognito_client):
    """Test login with invalid credentials"""
    from backend.src.auth.handler import handle_login
    
    error = ClientError(
        {'Error': {'Code': 'NotAuthorizedException', 'Message': 'Invalid'}},
        'InitiateAuth'
    )
    mock_cognito_client.initiate_auth.side_effect = error
    
    body = {
        'email': 'user@example.com',
        'password': 'WrongPassword'
    }
    
    response = handle_login(body)
    
    assert response['statusCode'] == 401
    body_data = json.loads(response['body'])
    assert 'Invalid credentials' in body_data['error']
