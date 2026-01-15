import json
import boto3
import os
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table(os.environ.get('SUBSCRIPTIONS_TABLE', 'Subscriptions'))

class GovernanceEngine:
    """
    Enforces governance rules and policies for the platform
    """
    
    def __init__(self):
        self.rules = {
            'rate_limiting': self._validate_rate_limit,
            'tier_access': self._validate_tier_access,
            'content_policy': self._validate_content_policy,
            'data_privacy': self._validate_data_privacy
        }
    
    def validate_request(self, user_id, membership_tier, request_data):
        """
        Validate request against all governance rules
        """
        violations = []
        
        for rule_name, rule_func in self.rules.items():
            try:
                is_valid, message = rule_func(user_id, membership_tier, request_data)
                if not is_valid:
                    violations.append({
                        'rule': rule_name,
                        'message': message
                    })
            except Exception as e:
                print(f"Error validating rule {rule_name}: {str(e)}")
                violations.append({
                    'rule': rule_name,
                    'message': f"Validation error: {str(e)}"
                })
        
        return {
            'valid': len(violations) == 0,
            'violations': violations
        }
    
    def _validate_rate_limit(self, user_id, membership_tier, request_data):
        """
        Validate rate limiting based on membership tier
        """
        # Define rate limits per tier (requests per minute)
        rate_limits = {
            'Free': 2,
            'Pro': 10,
            'Enterprise': 50
        }
        
        limit = rate_limits.get(membership_tier, 2)
        
        # In production, this would check against a rate limiting service
        # For now, we'll return True
        return True, "Rate limit check passed"
    
    def _validate_tier_access(self, user_id, membership_tier, request_data):
        """
        Validate that user's tier allows the requested service
        """
        category = request_data.get('category')
        
        tier_access = {
            'Free': ['consulting', 'technical'],
            'Pro': ['consulting', 'technical', 'creative'],
            'Enterprise': ['consulting', 'legal', 'technical', 'creative']
        }
        
        allowed_categories = tier_access.get(membership_tier, [])
        
        if category and category not in allowed_categories:
            return False, f"Category '{category}' not available for {membership_tier} tier"
        
        return True, "Tier access validated"
    
    def _validate_content_policy(self, user_id, membership_tier, request_data):
        """
        Validate content against platform policies
        """
        prompt = request_data.get('requestData', {}).get('prompt', '')
        
        # Basic content filtering (in production, use more sophisticated filtering)
        prohibited_keywords = ['illegal', 'harmful', 'unethical']
        
        prompt_lower = prompt.lower()
        for keyword in prohibited_keywords:
            if keyword in prompt_lower:
                return False, f"Content policy violation: prohibited content detected"
        
        return True, "Content policy validated"
    
    def _validate_data_privacy(self, user_id, membership_tier, request_data):
        """
        Validate data privacy requirements
        """
        # Check for PII in requests
        request_str = str(request_data)
        
        # Basic PII patterns (in production, use more sophisticated detection)
        pii_patterns = ['ssn', 'social security', 'credit card']
        
        request_lower = request_str.lower()
        for pattern in pii_patterns:
            if pattern in request_lower:
                return False, "Data privacy violation: PII detected in request"
        
        return True, "Data privacy validated"

def lambda_handler(event, context):
    """
    Handle governance validation requests
    """
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Get user info
        user_claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        user_id = user_claims.get('sub')
        
        # Get membership tier
        membership_tier = body.get('membershipTier', 'Free')
        request_data = body.get('requestData', {})
        
        # Create governance engine and validate
        engine = GovernanceEngine()
        validation_result = engine.validate_request(user_id, membership_tier, request_data)
        
        if validation_result['valid']:
            return response(200, {
                'status': 'approved',
                'message': 'Request passed all governance checks'
            })
        else:
            return response(403, {
                'status': 'rejected',
                'violations': validation_result['violations']
            })
        
    except Exception as e:
        print(f"Error in governance validation: {str(e)}")
        return response(500, {'error': 'Governance validation failed'})

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
