"""
Utility functions for backend services
"""

import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    """
    Helper class to convert DynamoDB Decimal objects to JSON
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def json_response(status_code, body, headers=None):
    """
    Create a standardized API Gateway response
    
    Args:
        status_code: HTTP status code
        body: Response body (dict or string)
        headers: Optional additional headers
    
    Returns:
        API Gateway response dict
    """
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': True
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body, cls=DecimalEncoder) if isinstance(body, dict) else body
    }


def extract_user_info(event):
    """
    Extract user information from Cognito authorizer context
    
    Args:
        event: Lambda event object
    
    Returns:
        dict with user_id, email, and other claims
    """
    claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
    
    return {
        'user_id': claims.get('sub'),
        'email': claims.get('email'),
        'username': claims.get('cognito:username'),
        'claims': claims
    }


def validate_required_fields(body, required_fields):
    """
    Validate that required fields are present in request body
    
    Args:
        body: Request body dict
        required_fields: List of required field names
    
    Returns:
        tuple (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in body or not body[field]]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None
