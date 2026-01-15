# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                          │
│  ┌────────────┐  ┌────────────────┐  ┌──────────────────┐      │
│  │   Login    │  │ Service        │  │  Subscription    │      │
│  │ Component  │  │ Selector       │  │  Manager         │      │
│  └────────────┘  └────────────────┘  └──────────────────┘      │
│         │                │                      │                │
│         └────────────────┴──────────────────────┘                │
│                          │                                       │
│                   [API Services]                                 │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  API GATEWAY (REST API)                          │
│                  ┌─────────────────────┐                         │
│                  │  Cognito Authorizer │                         │
│                  └─────────────────────┘                         │
└──────────┬────────────┬─────────────┬────────────┬──────────────┘
           │            │             │            │
     ┌─────▼─────┐ ┌───▼────┐  ┌────▼─────┐ ┌───▼──────┐
     │   Auth    │ │Service │  │  Agent   │ │Governance│
     │  Lambda   │ │Router  │  │Orchestr. │ │ Validator│
     └─────┬─────┘ └───┬────┘  └────┬─────┘ └───┬──────┘
           │           │             │            │
           ▼           ▼             ▼            ▼
┌──────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐      │
│  │   Cognito    │  │  DynamoDB    │  │   DynamoDB       │      │
│  │  User Pool   │  │  Services    │  │ Subscriptions    │      │
│  └──────────────┘  └──────────────┘  └──────────────────┘      │
└──────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                EXTERNAL AI SERVICES                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │Consulting│  │  Legal   │  │Technical │  │ Creative │        │
│  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer

**Technology**: React 18
**Responsibilities**:
- User interface for authentication
- Service selection and request submission
- Subscription management
- Token management and API communication

**Key Components**:
1. **Login Component**: User authentication UI
2. **ServiceSelector**: Display and select from 4 service categories
3. **SubscriptionManager**: Tier management and upgrades

### API Gateway Layer

**Technology**: AWS API Gateway (REST API)
**Responsibilities**:
- Request routing
- Authentication via Cognito
- CORS handling
- Request/response transformation

**Security**:
- JWT token validation
- Rate limiting
- Request throttling

### Lambda Functions Layer

#### 1. Auth Function
**Purpose**: Handle user authentication
**Endpoints**:
- POST /auth/register
- POST /auth/login

**Operations**:
- User registration with default Free tier
- User authentication
- Token generation via Cognito

#### 2. Service Router Function
**Purpose**: Route service requests to appropriate handlers
**Endpoints**:
- GET /services
- POST /services/request

**Operations**:
- List available services by tier
- Validate service availability
- Check usage limits
- Route to agent orchestrator

#### 3. Agent Orchestrator Function
**Purpose**: Manage AI agent interactions
**Endpoints**:
- POST /agents/process

**Operations**:
- Route requests to specialized AI agents
- Format AI requests/responses
- Track usage
- Handle AI API errors

#### 4. Governance Validator Function
**Purpose**: Enforce platform policies
**Endpoints**:
- POST /governance/validate

**Operations**:
- Rate limit validation
- Tier access control
- Content policy enforcement
- Data privacy checks

#### 5. Subscription Manager Function
**Purpose**: Manage user subscriptions
**Endpoints**:
- GET /subscription
- PUT /subscription

**Operations**:
- Get subscription details
- Update membership tier
- Enforce quotas
- Track usage

### Data Layer

#### AWS Cognito User Pool
**Purpose**: User management and authentication
**Schema**:
- Standard attributes (email, password)
- Custom attributes (membershipTier)

#### DynamoDB - Services Table
**Purpose**: Store service metadata
**Schema**:
```
{
  serviceId: String (Partition Key),
  category: String (GSI),
  name: String,
  description: String,
  agentType: String,
  metadata: Map
}
```

#### DynamoDB - Subscriptions Table
**Purpose**: Track user subscriptions and usage
**Schema**:
```
{
  userId: String (Partition Key),
  membershipTier: String,
  requestLimit: Number,
  requestsThisMonth: Number,
  status: String,
  createdAt: String,
  updatedAt: String
}
```

### AI Agent Layer

**Purpose**: External AI service integration
**Agents**:
1. **Consulting Agent**: Business strategy and planning
2. **Legal Agent**: Legal document analysis
3. **Technical Agent**: Technical problem solving
4. **Creative Agent**: Content creation

**Integration**: Framework for connecting to OpenAI, Anthropic, or custom AI services

## Data Flow

### User Registration Flow
```
1. User submits email/password → Frontend
2. Frontend → POST /auth/register → Auth Lambda
3. Auth Lambda → Create user → Cognito
4. Cognito → Return user ID
5. Auth Lambda → Create subscription → DynamoDB
6. Return success → Frontend
```

### Service Request Flow
```
1. User selects service + enters prompt → Frontend
2. Frontend → POST /services/request → Service Router
3. Service Router → Validate tier/limits → Subscriptions DB
4. Service Router → POST /governance/validate → Governance Lambda
5. Governance Lambda → Validate rules → Return approval
6. Service Router → POST /agents/process → Agent Orchestrator
7. Agent Orchestrator → Call AI Agent → External AI Service
8. AI Response → Format → Return to Frontend
9. Update usage count → Subscriptions DB
```

### Subscription Update Flow
```
1. User selects new tier → Frontend
2. Frontend → PUT /subscription → Subscription Manager
3. Subscription Manager → Validate tier
4. Update DynamoDB → Subscriptions table
5. Update Cognito → User attributes
6. Return confirmation → Frontend
```

## Security Architecture

### Authentication & Authorization
- **Cognito**: Manages user identities
- **JWT Tokens**: Secure API access
- **API Gateway Authorizer**: Validates tokens on each request

### Data Security
- **Encryption at rest**: DynamoDB encryption
- **Encryption in transit**: HTTPS/TLS
- **IAM Roles**: Least privilege access

### Governance Controls
- **Rate Limiting**: Prevent abuse
- **Content Filtering**: Block prohibited content
- **PII Detection**: Protect sensitive data
- **Tier Enforcement**: Ensure proper access

## Scalability

### Auto-scaling Components
- **Lambda Functions**: Automatic scaling
- **DynamoDB**: On-demand or provisioned capacity
- **API Gateway**: Handles high request volumes
- **Cognito**: Scales automatically

### Performance Optimization
- **Lambda Cold Starts**: Provisioned concurrency option
- **DynamoDB GSI**: Fast category lookups
- **Caching**: CloudFront for frontend
- **Connection Pooling**: Reuse connections

## High Availability

### AWS Regions
- Deploy across multiple Availability Zones
- CloudFront for global distribution
- Route 53 for DNS failover

### Monitoring
- **CloudWatch Logs**: All Lambda logs
- **CloudWatch Metrics**: Custom metrics
- **X-Ray**: Distributed tracing
- **Alarms**: Error rate, latency, throttling

## Cost Optimization

### Pay-per-use Services
- Lambda: Billed per invocation
- API Gateway: Per request
- DynamoDB: On-demand pricing recommended
- Cognito: Free tier for first 50k users

### Estimated Monthly Cost (Low Traffic)
- API Gateway: $3.50/1M requests
- Lambda: $0.20/1M requests  
- DynamoDB: $1.25 for 1GB storage
- Cognito: Free (under 50k MAU)
- **Total**: ~$5-10/month for small scale

## Deployment Model

### Infrastructure as Code
- **AWS SAM**: CloudFormation-based
- **Declarative**: Infrastructure in YAML
- **Versioned**: Git-tracked infrastructure

### CI/CD Pipeline (Future)
```
Code → GitHub → GitHub Actions → Build → Test → Deploy → Production
```

## Integration Points

### External Services
1. **AI APIs**: OpenAI, Anthropic, Custom models
2. **Payment**: Stripe integration (future)
3. **Email**: SES for notifications (future)
4. **Analytics**: GA, Mixpanel (future)

### Webhook Support (Future)
- Event notifications
- Status updates
- Usage alerts

## Disaster Recovery

### Backup Strategy
- **DynamoDB**: Point-in-time recovery
- **Cognito**: User data export
- **CloudFormation**: Infrastructure versioning

### Recovery Time Objective (RTO)
- Target: < 1 hour
- Method: CloudFormation re-deployment

### Recovery Point Objective (RPO)
- Target: < 15 minutes
- Method: DynamoDB continuous backup

## Compliance Considerations

### Data Privacy
- **GDPR**: User data deletion on request
- **CCPA**: Data access and portability
- **PII Handling**: Governance rules for detection

### Security Standards
- **OWASP**: API security best practices
- **AWS Well-Architected**: Following AWS guidelines
- **SOC 2**: Audit trail in CloudTrail

## Future Enhancements

1. **Multi-region deployment**
2. **Advanced analytics dashboard**
3. **A/B testing framework**
4. **Custom AI model training**
5. **Mobile app (React Native)**
6. **GraphQL API option**
7. **Real-time notifications (WebSocket)**
8. **Advanced governance (ML-based content filtering)**
