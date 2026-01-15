import json
import boto3
import os
import requests
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table(os.environ.get('SUBSCRIPTIONS_TABLE', 'Subscriptions'))

class AIAgentOrchestrator:
    """
    Orchestrates requests to different AI agents based on service category
    """
    
    def __init__(self):
        self.agent_configs = {
            'consulting_agent': {
                'name': 'Business Consulting Agent',
                'endpoint': os.environ.get('CONSULTING_AGENT_ENDPOINT', 'https://api.example.com/consulting'),
                'model': 'gpt-4',
                'system_prompt': 'You are an expert business consultant providing strategic advice.'
            },
            'legal_agent': {
                'name': 'Legal Services Agent',
                'endpoint': os.environ.get('LEGAL_AGENT_ENDPOINT', 'https://api.example.com/legal'),
                'model': 'gpt-4',
                'system_prompt': 'You are a legal expert providing document review and legal guidance.'
            },
            'technical_agent': {
                'name': 'Technical Support Agent',
                'endpoint': os.environ.get('TECHNICAL_AGENT_ENDPOINT', 'https://api.example.com/technical'),
                'model': 'gpt-4',
                'system_prompt': 'You are a technical expert solving complex technical problems.'
            },
            'creative_agent': {
                'name': 'Creative Services Agent',
                'endpoint': os.environ.get('CREATIVE_AGENT_ENDPOINT', 'https://api.example.com/creative'),
                'model': 'gpt-4',
                'system_prompt': 'You are a creative professional providing content and creative solutions.'
            }
        }
    
    def process_request(self, agent_type, request_data, user_id):
        """
        Process request through appropriate AI agent
        """
        if agent_type not in self.agent_configs:
            raise ValueError(f"Invalid agent type: {agent_type}")
        
        agent_config = self.agent_configs[agent_type]
        
        # Prepare request for AI agent
        ai_request = {
            'prompt': request_data.get('prompt', ''),
            'context': request_data.get('context', {}),
            'system_prompt': agent_config['system_prompt'],
            'model': agent_config['model'],
            'user_id': user_id
        }
        
        try:
            # Call AI agent API (simulated for now)
            result = self._call_ai_agent(agent_config['endpoint'], ai_request)
            
            # Update usage tracking
            self._update_usage(user_id)
            
            return result
            
        except Exception as e:
            print(f"Error calling AI agent: {str(e)}")
            raise

    def _call_ai_agent(self, endpoint, request_data):
        """
        Make API call to AI agent service
        This is a framework - actual implementation would call real AI APIs
        """
        # For demo purposes, return a simulated response
        # In production, this would call OpenAI, Anthropic, or custom AI services
        
        return {
            'response': f"AI Agent processed your request: {request_data.get('prompt', '')}",
            'confidence': 0.95,
            'timestamp': datetime.utcnow().isoformat(),
            'model': request_data.get('model'),
            'tokens_used': 150
        }
        
        # Production implementation would be:
        # response = requests.post(
        #     endpoint,
        #     json=request_data,
        #     headers={'Authorization': f'Bearer {os.environ.get("AI_API_KEY")}'},
        #     timeout=30
        # )
        # return response.json()
    
    def _update_usage(self, user_id):
        """
        Update user's usage count in DynamoDB
        """
        try:
            subscriptions_table.update_item(
                Key={'userId': user_id},
                UpdateExpression='SET requestsThisMonth = if_not_exists(requestsThisMonth, :zero) + :inc',
                ExpressionAttributeValues={':inc': 1, ':zero': 0}
            )
        except Exception as e:
            print(f"Error updating usage: {str(e)}")

def lambda_handler(event, context):
    """
    Handle agent orchestration requests
    """
    try:
        body = json.loads(event.get('body', '{}'))
        
        agent_type = body.get('agentType')
        request_data = body.get('requestData', {})
        
        # Get user info
        user_claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        user_id = user_claims.get('sub')
        
        if not agent_type:
            return response(400, {'error': 'Agent type required'})
        
        # Create orchestrator and process request
        orchestrator = AIAgentOrchestrator()
        result = orchestrator.process_request(agent_type, request_data, user_id)
        
        return response(200, {
            'status': 'success',
            'result': result,
            'requestId': context.request_id
        })
        
    except ValueError as e:
        return response(400, {'error': str(e)})
    except Exception as e:
        print(f"Error in orchestrator: {str(e)}")
        return response(500, {'error': 'Failed to process request'})

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
