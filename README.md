# ACCESSMEIFYOUCAN

Multi-tenant SaaS platform for AI-powered professional services. Users can select services from 4 categories, with requests routed to appropriate AI agents with governance enforcement.

## Features

### 🔐 Authentication & Authorization
- AWS Cognito-based user authentication
- JWT token management
- Membership tiers: Free, Pro, Enterprise
- Secure registration and login

### 🎯 Service Categories (4)
1. **Business Consulting** 💼 - Strategic business advice and planning
2. **Legal Services** ⚖️ - Legal document review and advice (Enterprise only)
3. **Technical Support** 🔧 - Technical problem solving and guidance
4. **Creative Services** 🎨 - Content creation and creative solutions

### 🤖 AI Agent Orchestration
- Intelligent routing to specialized AI agents
- Service-specific agent configuration
- Response formatting and handling
- Usage tracking and analytics

### 🛡️ Governance System
- Rate limiting by membership tier
- Content policy validation
- Data privacy checks
- Tier-based access control

### 💳 Subscription Management
- Three membership tiers with different capabilities
- Usage quota enforcement
- Upgrade/downgrade functionality
- Billing integration hooks

## Architecture

### Tech Stack
- **Frontend**: React, Axios
- **Backend**: AWS Lambda (Python), Node.js
- **Infrastructure**: AWS SAM/CloudFormation
- **Database**: DynamoDB
- **Authentication**: AWS Cognito
- **API**: API Gateway with JWT authorization

### AWS Services
- **Cognito**: User authentication and management
- **Lambda**: Serverless compute for API endpoints
- **API Gateway**: RESTful API with Cognito authorization
- **DynamoDB**: NoSQL database for services and subscriptions
- **RDS**: Optional for relational data (future enhancement)

## Project Structure

```
ACCESSMEIFYOUCAN/
├── backend/
│   ├── src/
│   │   ├── auth/              # Authentication handlers
│   │   ├── services/          # Service routing logic
│   │   ├── agents/            # AI agent orchestration
│   │   ├── governance/        # Governance rules engine
│   │   └── subscriptions/     # Subscription management
│   ├── package.json
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API services
│   │   └── App.js            # Main application
│   ├── public/
│   └── package.json
├── infrastructure/
│   └── template.yaml         # AWS SAM template
└── README.md
```

## Membership Tiers

### Free Tier
- **Price**: $0/month
- **Requests**: 10 per month
- **Rate Limit**: 2 requests per minute
- **Services**: Business Consulting, Technical Support

### Pro Tier
- **Price**: $29.99/month
- **Requests**: 100 per month
- **Rate Limit**: 10 requests per minute
- **Services**: Business Consulting, Technical Support, Creative Services

### Enterprise Tier
- **Price**: $299.99/month
- **Requests**: Unlimited
- **Rate Limit**: 50 requests per minute
- **Services**: All services including Legal Services
- **Features**: Priority support

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login

### Services
- `GET /services` - Get available services
- `POST /services/request` - Request a service

### AI Agents
- `POST /agents/process` - Process request with AI agent

### Governance
- `POST /governance/validate` - Validate request against rules

### Subscription
- `GET /subscription` - Get user subscription
- `PUT /subscription` - Update subscription tier

## Setup Instructions

### Prerequisites
- AWS Account
- AWS CLI configured
- AWS SAM CLI installed
- Node.js 16+ and npm
- Python 3.11+

### Backend Deployment

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
npm install
```

2. Deploy infrastructure:
```bash
cd ../infrastructure
sam build
sam deploy --guided
```

3. Note the API endpoint and Cognito details from outputs

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env` file:
```
REACT_APP_API_URL=https://your-api-gateway-url.amazonaws.com/prod
```

3. Start development server:
```bash
npm start
```

## Environment Variables

### Backend Lambda Functions
- `USER_POOL_ID` - Cognito User Pool ID
- `USER_POOL_CLIENT_ID` - Cognito User Pool Client ID
- `SERVICES_TABLE` - DynamoDB Services table name
- `SUBSCRIPTIONS_TABLE` - DynamoDB Subscriptions table name
- `CONSULTING_AGENT_ENDPOINT` - AI agent endpoint (optional)
- `LEGAL_AGENT_ENDPOINT` - AI agent endpoint (optional)
- `TECHNICAL_AGENT_ENDPOINT` - AI agent endpoint (optional)
- `CREATIVE_AGENT_ENDPOINT` - AI agent endpoint (optional)

### Frontend
- `REACT_APP_API_URL` - API Gateway base URL

## Development

### Running Tests
```bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test
```

### Local Development
1. Use AWS SAM Local for backend testing:
```bash
sam local start-api
```

2. Run frontend in development mode:
```bash
cd frontend
npm start
```

## AI Agent Integration

The platform provides a flexible framework for integrating with various AI services:

1. **Agent Configuration**: Each agent type has configurable endpoints and models
2. **Request Routing**: Automatic routing based on service category
3. **Response Handling**: Standardized response format
4. **Usage Tracking**: Automatic tracking of AI API usage

To integrate real AI services (OpenAI, Anthropic, etc.):
1. Add API keys to environment variables
2. Update agent endpoints in `orchestrator.py`
3. Implement actual API calls in `_call_ai_agent` method

## Governance Rules

The platform enforces multiple governance policies:

1. **Rate Limiting**: Prevents abuse by limiting requests per minute
2. **Tier Access Control**: Ensures users only access allowed services
3. **Content Policy**: Filters prohibited content
4. **Data Privacy**: Detects and blocks PII in requests

## Security

- All API endpoints (except auth) require JWT authentication
- Passwords stored securely in AWS Cognito
- CORS configured for frontend origin
- Content validation on all requests
- Rate limiting to prevent abuse

## Monitoring

Consider adding:
- CloudWatch Logs for Lambda functions
- CloudWatch Metrics for API Gateway
- X-Ray for distributed tracing
- Custom metrics for usage tracking

## Future Enhancements

- [ ] Payment integration (Stripe)
- [ ] Email notifications
- [ ] Admin dashboard
- [ ] Analytics and reporting
- [ ] Webhooks for events
- [ ] API rate limiting with Redis
- [ ] Multi-region deployment
- [ ] Custom AI model training

## Support

For issues and questions:
1. Check the documentation
2. Review CloudWatch logs
3. Open an issue in the repository

## License

MIT License - See LICENSE file for details