# API Documentation

## Base URL

```
https://{api-gateway-id}.execute-api.{region}.amazonaws.com/prod
```

## Authentication

Most endpoints require JWT authentication via AWS Cognito. Include the access token in the Authorization header:

```
Authorization: Bearer {access_token}
```

## Endpoints

### Authentication

#### Register User

**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "userId": "uuid-here",
  "membershipTier": "Free"
}
```

**Errors:**
- `400` - Missing email or password
- `409` - User already exists

#### Login

**POST** `/auth/login`

Authenticate user and receive tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "accessToken": "jwt-access-token",
  "idToken": "jwt-id-token",
  "refreshToken": "jwt-refresh-token",
  "expiresIn": 3600,
  "membershipTier": "Free"
}
```

**Errors:**
- `400` - Missing credentials
- `401` - Invalid credentials

---

### Services

#### Get Available Services

**GET** `/services`

Get list of available service categories for the authenticated user.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "services": [
    {
      "categoryId": "consulting",
      "name": "Business Consulting",
      "description": "Strategic business advice and planning",
      "available": true
    },
    {
      "categoryId": "legal",
      "name": "Legal Services",
      "description": "Legal document review and advice",
      "available": false
    },
    {
      "categoryId": "technical",
      "name": "Technical Support",
      "description": "Technical problem solving and guidance",
      "available": true
    },
    {
      "categoryId": "creative",
      "name": "Creative Services",
      "description": "Content creation and creative solutions",
      "available": false
    }
  ],
  "membershipTier": "Free"
}
```

#### Request Service

**POST** `/services/request`

Submit a request for AI service processing.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "category": "consulting",
  "requestData": {
    "prompt": "I need help creating a business plan for a tech startup",
    "context": {
      "industry": "technology",
      "budget": "50000"
    }
  }
}
```

**Response (200):**
```json
{
  "status": "accepted",
  "requestId": "uuid-category-timestamp",
  "category": "consulting",
  "agentType": "consulting_agent",
  "message": "Request routed to AI agent for processing"
}
```

**Errors:**
- `400` - Invalid service category
- `403` - Service not available for membership tier
- `429` - Usage limit exceeded

---

### AI Agents

#### Process with Agent

**POST** `/agents/process`

Process a request through an AI agent.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "agentType": "consulting_agent",
  "requestData": {
    "prompt": "I need help creating a business plan for a tech startup",
    "context": {}
  }
}
```

**Response (200):**
```json
{
  "status": "success",
  "result": {
    "response": "AI Agent processed your request: I need help creating a business plan for a tech startup",
    "confidence": 0.95,
    "timestamp": "2026-01-15T10:00:00.000Z",
    "model": "gpt-4",
    "tokens_used": 150
  },
  "requestId": "lambda-request-id"
}
```

**Errors:**
- `400` - Invalid agent type or missing data
- `500` - Processing failed

---

### Governance

#### Validate Request

**POST** `/governance/validate`

Validate a request against governance rules.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "membershipTier": "Free",
  "requestData": {
    "category": "consulting",
    "requestData": {
      "prompt": "Business consultation request"
    }
  }
}
```

**Response (200 - Approved):**
```json
{
  "status": "approved",
  "message": "Request passed all governance checks"
}
```

**Response (403 - Rejected):**
```json
{
  "status": "rejected",
  "violations": [
    {
      "rule": "tier_access",
      "message": "Category 'legal' not available for Free tier"
    }
  ]
}
```

---

### Subscription

#### Get Subscription

**GET** `/subscription`

Get current user's subscription details.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "subscription": {
    "userId": "user-uuid",
    "membershipTier": "Free",
    "price": 0,
    "requestLimit": 10,
    "requestsThisMonth": 5,
    "features": ["consulting", "technical"],
    "rateLimit": 2,
    "status": "active",
    "createdAt": "2026-01-01T00:00:00.000Z",
    "updatedAt": "2026-01-15T10:00:00.000Z"
  }
}
```

#### Update Subscription

**PUT** `/subscription`

Update user's subscription tier.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "membershipTier": "Pro"
}
```

**Response (200):**
```json
{
  "message": "Subscription upgraded successfully",
  "subscription": {
    "membershipTier": "Pro",
    "price": 29.99,
    "requestLimit": 100,
    "features": ["consulting", "technical", "creative"],
    "status": "active"
  }
}
```

**Errors:**
- `400` - Invalid membership tier

---

## Service Categories

| Category   | ID          | Free | Pro | Enterprise |
|------------|-------------|------|-----|------------|
| Consulting | `consulting`| ✓    | ✓   | ✓          |
| Legal      | `legal`     | ✗    | ✗   | ✓          |
| Technical  | `technical` | ✓    | ✓   | ✓          |
| Creative   | `creative`  | ✗    | ✓   | ✓          |

## Rate Limits

| Tier       | Requests/Minute | Monthly Limit |
|------------|-----------------|---------------|
| Free       | 2               | 10            |
| Pro        | 10              | 100           |
| Enterprise | 50              | Unlimited     |

## Error Codes

| Code | Description                    |
|------|--------------------------------|
| 200  | Success                        |
| 201  | Created                        |
| 400  | Bad Request                    |
| 401  | Unauthorized                   |
| 403  | Forbidden                      |
| 409  | Conflict                       |
| 429  | Too Many Requests              |
| 500  | Internal Server Error          |

## Common Error Response Format

```json
{
  "error": "Error message describing what went wrong"
}
```

## Governance Rules

### Rate Limiting
Enforced per membership tier. Exceeding limits returns `429 Too Many Requests`.

### Tier Access Control
Services are restricted based on membership tier. Unauthorized access returns `403 Forbidden`.

### Content Policy
Requests containing prohibited content are rejected with policy violation details.

### Data Privacy
Requests containing PII (personally identifiable information) are flagged and may be rejected.

## Integration Examples

### JavaScript (Axios)

```javascript
import axios from 'axios';

const API_BASE = 'https://api.example.com/prod';
const token = 'your-access-token';

// Get services
const services = await axios.get(`${API_BASE}/services`, {
  headers: { Authorization: `Bearer ${token}` }
});

// Request service
const result = await axios.post(
  `${API_BASE}/services/request`,
  {
    category: 'consulting',
    requestData: { prompt: 'Help me with business strategy' }
  },
  { headers: { Authorization: `Bearer ${token}` } }
);
```

### Python (Requests)

```python
import requests

API_BASE = 'https://api.example.com/prod'
token = 'your-access-token'
headers = {'Authorization': f'Bearer {token}'}

# Get services
response = requests.get(f'{API_BASE}/services', headers=headers)
services = response.json()

# Request service
payload = {
    'category': 'consulting',
    'requestData': {'prompt': 'Help me with business strategy'}
}
response = requests.post(
    f'{API_BASE}/services/request',
    json=payload,
    headers=headers
)
result = response.json()
```

### cURL

```bash
# Register
curl -X POST https://api.example.com/prod/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass123!"}'

# Login
curl -X POST https://api.example.com/prod/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass123!"}'

# Get services (with token)
curl -X GET https://api.example.com/prod/services \
  -H "Authorization: Bearer YOUR_TOKEN"

# Request service
curl -X POST https://api.example.com/prod/services/request \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"category":"consulting","requestData":{"prompt":"Business help"}}'
```

## Pagination

Currently not implemented. Future versions may include pagination for listing endpoints.

## Versioning

Current API version: `v1` (included in base path as `/prod`)

Future versions will be accessible via `/v2`, `/v3`, etc.

## Support

For API questions or issues:
- Review this documentation
- Check CloudWatch logs
- Open an issue in the repository
