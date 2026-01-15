import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
services_table = dynamodb.Table(os.environ.get('SERVICES_TABLE', 'Services'))
subscriptions_table = dynamodb.Table(os.environ.get('SUBSCRIPTIONS_TABLE', 'Subscriptions'))

# Define 4 service categories
SERVICE_CATEGORIES = {
    'consulting': {
        'name': 'Business Consulting',
        'description': 'Strategic business advice and planning',
        'agentType': 'consulting_agent'
    },
    'legal': {
        'name': 'Legal Services',
        'description': 'Legal document review and advice',
        'agentType': 'legal_agent'
    },
    'technical': {
        'name': 'Technical Support',
        'description': 'Technical problem solving and guidance',
        'agentType': 'technical_agent'
    },
    'creative': {
        'name': 'Creative Services',
        'description': 'Content creation and creative solutions',
        'agentType': 'creative_agent'
    }
}

def lambda_handler(event, context):
    """
    Handle service routing requests
    """
    try:
        http_method = event.get('httpMethod')
        path = event.get('path', '')
        
        if http_method == 'GET' and path.endswith('/services'):
            return get_services(event)
        elif http_method == 'POST' and path.endswith('/services/request'):
            return request_service(event, context)
        else:
            return response(400, {'error': 'Invalid endpoint'})
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': str(e)})

def get_services(event):
    """
    Get list of available services by category
    """
    try:
        # Get user info from Cognito authorizer
        user_claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        user_id = user_claims.get('sub')
        
        # Get user subscription to determine available services
        subscription = get_user_subscription(user_id)
        membership_tier = subscription.get('membershipTier', 'Free')
        
        # Get all services
        services = []
        for category_id, category_info in SERVICE_CATEGORIES.items():
            services.append({
                'categoryId': category_id,
                'name': category_info['name'],
                'description': category_info['description'],
                'available': check_service_availability(category_id, membership_tier)
            })
        
        return response(200, {
            'services': services,
            'membershipTier': membership_tier
        })
        
    except Exception as e:
        print(f"Error getting services: {str(e)}")
        return response(500, {'error': 'Failed to retrieve services'})

def request_service(event, context):
    """
    Route service request to appropriate AI agent
    """
    try:
        body = json.loads(event.get('body', '{}'))
        category = body.get('category')
        request_data = body.get('requestData', {})
        
        # Get user info
        user_claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        user_id = user_claims.get('sub')
        
        # Validate category
        if category not in SERVICE_CATEGORIES:
            return response(400, {'error': 'Invalid service category'})
        
        # Check user subscription and limits
        subscription = get_user_subscription(user_id)
        membership_tier = subscription.get('membershipTier', 'Free')
        
        if not check_service_availability(category, membership_tier):
            return response(403, {
                'error': 'Service not available for your membership tier',
                'requiredTier': 'Pro or Enterprise'
            })
        
        # Check usage limits
        if not check_usage_limits(user_id, membership_tier):
            return response(429, {
                'error': 'Usage limit exceeded',
                'message': 'Please upgrade your membership tier'
            })
        
        # Route to agent orchestrator
        agent_type = SERVICE_CATEGORIES[category]['agentType']
        
        return response(200, {
            'status': 'accepted',
            'requestId': f"{user_id}_{category}_{context.request_id}",
            'category': category,
            'agentType': agent_type,
            'message': 'Request routed to AI agent for processing'
        })
        
    except Exception as e:
        print(f"Error processing service request: {str(e)}")
        return response(500, {'error': 'Failed to process request'})

def get_user_subscription(user_id):
    """
    Get user subscription details from DynamoDB
    """
    try:
        result = subscriptions_table.get_item(Key={'userId': user_id})
        if 'Item' in result:
            return result['Item']
        else:
            # Create default subscription if not exists
            default_subscription = {
                'userId': user_id,
                'membershipTier': 'Free',
                'requestsThisMonth': 0,
                'requestLimit': 10
            }
            subscriptions_table.put_item(Item=default_subscription)
            return default_subscription
    except Exception as e:
        print(f"Error getting subscription: {str(e)}")
        return {'membershipTier': 'Free', 'requestsThisMonth': 0, 'requestLimit': 10}

def check_service_availability(category, membership_tier):
    """
    Check if service is available for membership tier
    """
    # Free tier: Only consulting and technical
    # Pro tier: All except legal
    # Enterprise tier: All services
    
    tier_access = {
        'Free': ['consulting', 'technical'],
        'Pro': ['consulting', 'technical', 'creative'],
        'Enterprise': ['consulting', 'legal', 'technical', 'creative']
    }
    
    allowed_categories = tier_access.get(membership_tier, [])
    return category in allowed_categories

def check_usage_limits(user_id, membership_tier):
    """
    Check if user has exceeded usage limits
    """
    tier_limits = {
        'Free': 10,
        'Pro': 100,
        'Enterprise': -1  # Unlimited
    }
    
    limit = tier_limits.get(membership_tier, 10)
    
    if limit == -1:  # Unlimited
        return True
    
    try:
        subscription = subscriptions_table.get_item(Key={'userId': user_id})
        if 'Item' in subscription:
            requests_count = subscription['Item'].get('requestsThisMonth', 0)
            return requests_count < limit
        return True
    except Exception as e:
        print(f"Error checking limits: {str(e)}")
        return True  # Allow on error

def response(status_code, body):
    """
    Return formatted API Gateway response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True
        },
        'body': json.dumps(body)
    }
