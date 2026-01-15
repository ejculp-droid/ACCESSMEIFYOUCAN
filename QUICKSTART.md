# Quick Start Guide

Get up and running with ACCESSMEIFYOUCAN in under 30 minutes!

## Prerequisites Check

Before starting, verify you have:

```bash
# Check AWS CLI
aws --version
# Expected: aws-cli/2.x.x or higher

# Check Node.js
node --version
# Expected: v16.x.x or higher

# Check Python
python3 --version
# Expected: Python 3.11.x or higher

# Check AWS SAM CLI
sam --version
# Expected: SAM CLI, version 1.x.x or higher
```

If any are missing, install them first:
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Node.js](https://nodejs.org/)
- [Python](https://www.python.org/downloads/)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)

## Step 1: Clone Repository

```bash
git clone https://github.com/ejculp-droid/ACCESSMEIFYOUCAN.git
cd ACCESSMEIFYOUCAN
```

## Step 2: Configure AWS

```bash
# Configure AWS credentials
aws configure

# Enter when prompted:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)
```

## Step 3: Deploy Backend

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt
npm install
cd ..

# Deploy infrastructure
cd infrastructure
sam build

# Deploy (follow prompts)
sam deploy --guided
```

**During deployment, enter:**
- Stack name: `accessmeifyoucan-stack`
- AWS Region: Your preferred region
- Confirm changes: Y
- Allow SAM to create roles: Y
- Save arguments: Y

**Save these outputs:**
- ApiEndpoint
- UserPoolId
- UserPoolClientId

## Step 4: Setup Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
REACT_APP_API_URL=YOUR_API_ENDPOINT_FROM_STEP_3
EOF

# Replace YOUR_API_ENDPOINT_FROM_STEP_3 with actual endpoint
# Example: https://abc123.execute-api.us-east-1.amazonaws.com/prod
```

## Step 5: Start Frontend

```bash
npm start
```

Your browser should open to `http://localhost:3000`

## Step 6: Test the Platform

### Register a User

1. Click "Need an account? Register"
2. Enter email: `test@example.com`
3. Enter password: `Test123!@#`
4. Click "Register"
5. You'll see "Registration successful!"

### Login

1. Enter the same email and password
2. Click "Login"
3. You'll be redirected to the services page

### Try a Service

1. You'll see 4 service cards
2. Click on "Business Consulting" (available in Free tier)
3. Enter a prompt: "Help me create a business plan"
4. Click "Submit Request"
5. View the AI response

### Check Subscription

1. Click "Subscription" in the navigation
2. View your current plan (Free)
3. Try upgrading to Pro or Enterprise
4. Observe new services become available

## Troubleshooting

### Issue: "sam: command not found"
**Solution:** Install AWS SAM CLI
```bash
pip install aws-sam-cli
```

### Issue: Deployment fails with permissions error
**Solution:** Ensure AWS credentials have appropriate permissions
- IAM Full Access
- Lambda Full Access
- API Gateway Full Access
- DynamoDB Full Access
- Cognito Full Access

### Issue: Frontend can't connect to API
**Solution:** Check .env file has correct API endpoint
```bash
cat frontend/.env
# Should show: REACT_APP_API_URL=https://...
```

### Issue: CORS errors in browser
**Solution:** Verify API Gateway CORS is configured
- Check CloudFormation template has CORS settings
- Ensure API Gateway has OPTIONS method

### Issue: 401 Unauthorized errors
**Solution:** Check Cognito configuration
```bash
aws cognito-idp describe-user-pool --user-pool-id YOUR_POOL_ID
```

## Next Steps

### Customize the Platform

1. **Add real AI integration:**
   - Update `backend/src/agents/orchestrator.py`
   - Add API keys to environment variables
   - Implement actual AI API calls

2. **Customize styling:**
   - Edit component styles in `frontend/src/components/`
   - Add custom CSS files
   - Integrate UI framework (Material-UI, Tailwind)

3. **Add features:**
   - Email notifications
   - Payment integration
   - Analytics dashboard
   - Admin panel

### Explore the Code

```bash
# Backend structure
backend/
├── src/
│   ├── auth/           # Authentication logic
│   ├── services/       # Service routing
│   ├── agents/         # AI orchestration
│   ├── governance/     # Rules engine
│   └── subscriptions/  # Tier management

# Frontend structure
frontend/
├── src/
│   ├── components/     # React components
│   └── services/       # API clients
```

### Run Tests

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

### View Logs

```bash
# View Lambda logs
sam logs -n AuthFunction --stack-name accessmeifyoucan-stack --tail

# View all logs
aws logs tail /aws/lambda/accessmeifyoucan --follow
```

## Common Commands

```bash
# Redeploy backend after changes
cd infrastructure && sam build && sam deploy

# Rebuild frontend
cd frontend && npm run build

# View CloudFormation stack
aws cloudformation describe-stacks --stack-name accessmeifyoucan-stack

# Delete everything
aws cloudformation delete-stack --stack-name accessmeifyoucan-stack
```

## Resources

- **Full Documentation:** [README.md](README.md)
- **API Reference:** [API.md](API.md)
- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

## Getting Help

- Check documentation files
- Search existing GitHub issues
- Open a new issue with details
- Include logs and error messages

## Success Checklist

- [ ] Backend deployed successfully
- [ ] Frontend running locally
- [ ] User registration works
- [ ] User login works
- [ ] Services display correctly
- [ ] Service requests work
- [ ] Subscription management works
- [ ] Governance rules enforced

Congratulations! 🎉 You now have a working multi-tenant AI SaaS platform!

## What You've Built

You now have:
- ✅ Complete authentication system
- ✅ 4 AI service categories
- ✅ 3 membership tiers
- ✅ Governance rule engine
- ✅ Usage tracking and limits
- ✅ Scalable serverless backend
- ✅ Modern React frontend

Ready for production? Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment guide.
