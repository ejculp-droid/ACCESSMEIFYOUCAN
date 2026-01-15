"""
Unit tests for service router
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv('SERVICES_TABLE', 'test-services-table')
    monkeypatch.setenv('SUBSCRIPTIONS_TABLE', 'test-subscriptions-table')


@pytest.fixture
def mock_dynamodb():
    """Mock DynamoDB resource"""
    with patch('backend.src.services.router.dynamodb') as mock:
        yield mock


@pytest.fixture
def sample_event():
    """Sample API Gateway event"""
    return {
        'httpMethod': 'GET',
        'path': '/services',
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'user-123',
                    'email': 'user@example.com'
                }
            }
        }
    }


def test_get_services_success(mock_dynamodb, sample_event):
    """Test getting available services"""
    from backend.src.services.router import get_services
    
    # Mock subscription table response
    mock_table = MagicMock()
    mock_table.get_item.return_value = {
        'Item': {
            'userId': 'user-123',
            'membershipTier': 'Pro',
            'requestsThisMonth': 5
        }
    }
    mock_dynamodb.Table.return_value = mock_table
    
    response = get_services(sample_event)
    
    assert response['statusCode'] == 200
    body_data = json.loads(response['body'])
    assert 'services' in body_data
    assert len(body_data['services']) == 4
    assert body_data['membershipTier'] == 'Pro'


def test_check_service_availability():
    """Test service availability by tier"""
    from backend.src.services.router import check_service_availability
    
    # Free tier
    assert check_service_availability('consulting', 'Free') == True
    assert check_service_availability('technical', 'Free') == True
    assert check_service_availability('creative', 'Free') == False
    assert check_service_availability('legal', 'Free') == False
    
    # Pro tier
    assert check_service_availability('creative', 'Pro') == True
    assert check_service_availability('legal', 'Pro') == False
    
    # Enterprise tier
    assert check_service_availability('legal', 'Enterprise') == True


def test_request_service_success(mock_dynamodb):
    """Test successful service request"""
    from backend.src.services.router import request_service
    
    # Mock subscription table response
    mock_table = MagicMock()
    mock_table.get_item.return_value = {
        'Item': {
            'userId': 'user-123',
            'membershipTier': 'Pro',
            'requestsThisMonth': 5,
            'requestLimit': 100
        }
    }
    mock_dynamodb.Table.return_value = mock_table
    
    event = {
        'body': json.dumps({
            'category': 'consulting',
            'requestData': {
                'prompt': 'Help with business strategy'
            }
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'user-123'
                }
            }
        }
    }
    
    # Mock context
    class MockContext:
        request_id = 'test-request-123'
    
    response = request_service(event)
    
    assert response['statusCode'] == 200
    body_data = json.loads(response['body'])
    assert body_data['status'] == 'accepted'
    assert 'requestId' in body_data


def test_request_service_unavailable(mock_dynamodb):
    """Test request for unavailable service"""
    from backend.src.services.router import request_service
    
    mock_table = MagicMock()
    mock_table.get_item.return_value = {
        'Item': {
            'userId': 'user-123',
            'membershipTier': 'Free',
            'requestsThisMonth': 5
        }
    }
    mock_dynamodb.Table.return_value = mock_table
    
    event = {
        'body': json.dumps({
            'category': 'legal',  # Not available for Free tier
            'requestData': {'prompt': 'Legal advice'}
        }),
        'requestContext': {
            'authorizer': {
                'claims': {'sub': 'user-123'}
            }
        }
    }
    
    response = request_service(event)
    
    assert response['statusCode'] == 403
    body_data = json.loads(response['body'])
    assert 'not available' in body_data['error']
