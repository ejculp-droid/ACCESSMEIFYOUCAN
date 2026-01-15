import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table(os.environ.get('SUBSCRIPTIONS_TABLE', 'Subscriptions'))
cognito_client = boto3.client('cognito-idp')

MEMBERSHIP_TIERS = {
    'Free': {
        'price': 0,
        'requestLimit': 10,
        'features': ['consulting', 'technical'],
        'rateLimit': 2  # requests per minute
    },
    'Pro': {
        'price': 29.99,
        'requestLimit': 100,
        'features': ['consulting', 'technical', 'creative'],
        'rateLimit': 10
    },
    'Enterprise': {
        'price': 299.99,
        'requestLimit': -1,  # Unlimited
        'features': ['consulting', 'legal', 'technical', 'creative'],
        'rateLimit': 50
    }
}

def lambda_handler(event, context):
    """
    Handle subscription management requests
    """
    try:
        http_method = event.get('httpMethod')
        
        if http_method == 'GET':
            return get_subscription(event)
        elif http_method == 'PUT':
            return update_subscription(event)
        else:
            return response(400, {'error': 'Invalid method'})
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': str(e)})

def get_subscription(event):
    """
    Get user's current subscription details
    """
    try:
        # Get user info
        user_claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        user_id = user_claims.get('sub')
        
        # Get subscription from DynamoDB
        result = subscriptions_table.get_item(Key={'userId': user_id})
        
        if 'Item' in result:
            subscription = result['Item']
        else:
            # Create default subscription
            subscription = create_default_subscription(user_id)
        
        # Get tier details
        tier = subscription.get('membershipTier', 'Free')
        tier_details = MEMBERSHIP_TIERS.get(tier, MEMBERSHIP_TIERS['Free'])
        
        return response(200, {
            'subscription': {
                'userId': user_id,
                'membershipTier': tier,
                'price': tier_details['price'],
                'requestLimit': tier_details['requestLimit'],
                'requestsThisMonth': int(subscription.get('requestsThisMonth', 0)),
                'features': tier_details['features'],
                'rateLimit': tier_details['rateLimit'],
                'status': subscription.get('status', 'active'),
                'createdAt': subscription.get('createdAt', datetime.utcnow().isoformat()),
                'updatedAt': subscription.get('updatedAt', datetime.utcnow().isoformat())
            }
        })
        
    except Exception as e:
        print(f"Error getting subscription: {str(e)}")
        return response(500, {'error': 'Failed to retrieve subscription'})

def update_subscription(event):
    """
    Update user's subscription tier
    """
    try:
        body = json.loads(event.get('body', '{}'))
        new_tier = body.get('membershipTier')
        
        # Get user info
        user_claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        user_id = user_claims.get('sub')
        user_pool_id = os.environ.get('USER_POOL_ID')
        
        # Validate tier
        if new_tier not in MEMBERSHIP_TIERS:
            return response(400, {'error': 'Invalid membership tier'})
        
        # Get current subscription
        result = subscriptions_table.get_item(Key={'userId': user_id})
        current_subscription = result.get('Item', {})
        current_tier = current_subscription.get('membershipTier', 'Free')
        
        # Determine if upgrade or downgrade
        tier_order = ['Free', 'Pro', 'Enterprise']
        is_upgrade = tier_order.index(new_tier) > tier_order.index(current_tier)
        
        # Update subscription in DynamoDB
        tier_details = MEMBERSHIP_TIERS[new_tier]
        updated_subscription = {
            'userId': user_id,
            'membershipTier': new_tier,
            'requestLimit': tier_details['requestLimit'],
            'requestsThisMonth': current_subscription.get('requestsThisMonth', 0),
            'status': 'active',
            'updatedAt': datetime.utcnow().isoformat(),
            'createdAt': current_subscription.get('createdAt', datetime.utcnow().isoformat())
        }
        
        subscriptions_table.put_item(Item=updated_subscription)
        
        # Update Cognito user attributes
        try:
            cognito_client.admin_update_user_attributes(
                UserPoolId=user_pool_id,
                Username=user_id,
                UserAttributes=[
                    {'Name': 'custom:membershipTier', 'Value': new_tier}
                ]
            )
        except Exception as e:
            print(f"Error updating Cognito attributes: {str(e)}")
        
        return response(200, {
            'message': f'Subscription {"upgraded" if is_upgrade else "changed"} successfully',
            'subscription': {
                'membershipTier': new_tier,
                'price': tier_details['price'],
                'requestLimit': tier_details['requestLimit'],
                'features': tier_details['features'],
                'status': 'active'
            }
        })
        
    except Exception as e:
        print(f"Error updating subscription: {str(e)}")
        return response(500, {'error': 'Failed to update subscription'})

def create_default_subscription(user_id):
    """
    Create a default Free tier subscription
    """
    subscription = {
        'userId': user_id,
        'membershipTier': 'Free',
        'requestLimit': 10,
        'requestsThisMonth': 0,
        'status': 'active',
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat()
    }
    
    subscriptions_table.put_item(Item=subscription)
    return subscription

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
