import json
import boto3
import os
from botocore.exceptions import ClientError

cognito_client = boto3.client('cognito-idp')
USER_POOL_ID = os.environ.get('USER_POOL_ID')
USER_POOL_CLIENT_ID = os.environ.get('USER_POOL_CLIENT_ID')

def lambda_handler(event, context):
    """
    Handle authentication requests (register, login)
    """
    try:
        path = event.get('path', '')
        body = json.loads(event.get('body', '{}'))
        
        if path.endswith('/register'):
            return handle_register(body)
        elif path.endswith('/login'):
            return handle_login(body)
        else:
            return response(400, {'error': 'Invalid endpoint'})
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': str(e)})

def handle_register(body):
    """
    Register a new user with default Free tier
    """
    email = body.get('email')
    password = body.get('password')
    
    if not email or not password:
        return response(400, {'error': 'Email and password required'})
    
    try:
        # Create user in Cognito
        response_data = cognito_client.sign_up(
            ClientId=USER_POOL_CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'custom:membershipTier', 'Value': 'Free'}
            ]
        )
        
        return response(201, {
            'message': 'User registered successfully',
            'userId': response_data['UserSub'],
            'membershipTier': 'Free'
        })
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UsernameExistsException':
            return response(409, {'error': 'User already exists'})
        else:
            return response(400, {'error': e.response['Error']['Message']})

def handle_login(body):
    """
    Authenticate user and return tokens
    """
    email = body.get('email')
    password = body.get('password')
    
    if not email or not password:
        return response(400, {'error': 'Email and password required'})
    
    try:
        # Authenticate user
        auth_response = cognito_client.initiate_auth(
            ClientId=USER_POOL_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        
        # Get user attributes
        access_token = auth_response['AuthenticationResult']['AccessToken']
        user_info = cognito_client.get_user(AccessToken=access_token)
        
        # Extract membership tier
        membership_tier = 'Free'
        for attr in user_info['UserAttributes']:
            if attr['Name'] == 'custom:membershipTier':
                membership_tier = attr['Value']
                break
        
        return response(200, {
            'accessToken': auth_response['AuthenticationResult']['AccessToken'],
            'idToken': auth_response['AuthenticationResult']['IdToken'],
            'refreshToken': auth_response['AuthenticationResult']['RefreshToken'],
            'expiresIn': auth_response['AuthenticationResult']['ExpiresIn'],
            'membershipTier': membership_tier
        })
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NotAuthorizedException':
            return response(401, {'error': 'Invalid credentials'})
        else:
            return response(400, {'error': e.response['Error']['Message']})

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
