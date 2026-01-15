# Deployment Guide

## Prerequisites

Before deploying the ACCESSMEIFYOUCAN platform, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured (`aws configure`)
3. **AWS SAM CLI** installed (`pip install aws-sam-cli`)
4. **Node.js 16+** and npm
5. **Python 3.11+**

## Step-by-Step Deployment

### 1. Clone Repository

```bash
git clone https://github.com/ejculp-droid/ACCESSMEIFYOUCAN.git
cd ACCESSMEIFYOUCAN
```

### 2. Deploy Backend Infrastructure

#### Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
npm install
cd ..
```

#### Configure SAM

```bash
cd infrastructure
sam build
```

#### Deploy with Guided Mode

```bash
sam deploy --guided
```

When prompted, provide:
- **Stack Name**: `accessmeifyoucan-stack`
- **AWS Region**: Your preferred region (e.g., `us-east-1`)
- **Confirm changes before deploy**: Y
- **Allow SAM CLI IAM role creation**: Y
- **Save arguments to configuration file**: Y

#### Note the Outputs

After successful deployment, note these outputs:
- `ApiEndpoint` - Your API Gateway URL
- `UserPoolId` - Cognito User Pool ID
- `UserPoolClientId` - Cognito User Pool Client ID

### 3. Deploy Frontend

#### Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

#### Configure Environment

Create `.env` file in the `frontend` directory:

```env
REACT_APP_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/prod
```

Replace with your actual API Gateway endpoint from step 2.

#### Build Frontend

```bash
npm run build
```

#### Deploy to S3 + CloudFront (Optional)

For production deployment:

1. Create S3 bucket:
```bash
aws s3 mb s3://accessmeifyoucan-frontend
```

2. Configure bucket for static website hosting:
```bash
aws s3 website s3://accessmeifyoucan-frontend --index-document index.html --error-document index.html
```

3. Upload build files:
```bash
aws s3 sync build/ s3://accessmeifyoucan-frontend --acl public-read
```

4. Create CloudFront distribution (optional for CDN)

### 4. Test Deployment

#### Test Backend API

```bash
# Test health endpoint (if added)
curl https://your-api-endpoint/prod/services

# Should return 401 Unauthorized (expected, as authentication is required)
```

#### Test Frontend

```bash
# Run locally first
npm start
```

Visit `http://localhost:3000` and test:
1. User registration
2. User login
3. Service selection
4. Subscription management

## Configuration Updates

### Update Cognito Custom Attributes

If you need to add custom attributes to Cognito:

```bash
aws cognito-idp add-custom-attributes \
  --user-pool-id YOUR_USER_POOL_ID \
  --custom-attributes Name=membershipTier,AttributeDataType=String
```

### Update DynamoDB Tables

Tables are automatically created by SAM template. To modify:

1. Edit `infrastructure/template.yaml`
2. Run `sam build && sam deploy`

## Environment-Specific Configurations

### Development

```env
# frontend/.env.development
REACT_APP_API_URL=http://localhost:3000
```

### Production

```env
# frontend/.env.production
REACT_APP_API_URL=https://api.accessmeifyoucan.com/prod
```

## Post-Deployment Verification

### 1. Verify Cognito User Pool

```bash
aws cognito-idp describe-user-pool --user-pool-id YOUR_USER_POOL_ID
```

### 2. Verify DynamoDB Tables

```bash
aws dynamodb list-tables
```

### 3. Verify Lambda Functions

```bash
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'accessmeifyoucan')]"
```

### 4. Test API Gateway

```bash
# Test registration
curl -X POST https://your-api-endpoint/prod/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

## Troubleshooting

### Issue: Lambda Timeout

**Solution**: Increase timeout in `template.yaml`:
```yaml
Globals:
  Function:
    Timeout: 60  # Increase from 30
```

### Issue: CORS Errors

**Solution**: Verify CORS configuration in `template.yaml`:
```yaml
Cors:
  AllowOrigin: "'*'"  # Or specific domain for production
```

### Issue: Cognito Authentication Fails

**Solution**: Check User Pool Client settings:
- Ensure auth flows are enabled
- Verify redirect URLs
- Check app client secret setting (should be disabled for public clients)

### Issue: DynamoDB Access Denied

**Solution**: Verify IAM policies in Lambda functions have DynamoDB permissions.

## Monitoring Setup

### Enable CloudWatch Logs

Logs are automatically enabled for Lambda functions.

View logs:
```bash
sam logs -n AuthFunction --stack-name accessmeifyoucan-stack --tail
```

### Set Up Alarms

```bash
# Example: Lambda error alarm
aws cloudwatch put-metric-alarm \
  --alarm-name accessmeifyoucan-lambda-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

## Updating Deployment

### Update Backend

```bash
cd infrastructure
sam build
sam deploy  # No --guided flag needed after first deployment
```

### Update Frontend

```bash
cd frontend
npm run build
aws s3 sync build/ s3://accessmeifyoucan-frontend
```

## Rollback

If deployment fails:

```bash
aws cloudformation delete-stack --stack-name accessmeifyoucan-stack
```

Or rollback to previous version:

```bash
aws cloudformation update-stack --stack-name accessmeifyoucan-stack --use-previous-template
```

## Cost Estimation

Estimated monthly costs (low usage):
- **API Gateway**: ~$3.50/million requests
- **Lambda**: ~$0.20/million requests
- **DynamoDB**: ~$1.25 (on-demand pricing)
- **Cognito**: Free tier up to 50,000 MAUs
- **S3 + CloudFront**: ~$1-5 depending on traffic

**Total**: ~$5-10/month for low traffic

## Security Best Practices

1. **Enable WAF** on API Gateway for production
2. **Use custom domain** with SSL certificate
3. **Enable CloudTrail** for audit logging
4. **Set up VPC** for Lambda functions (if needed)
5. **Rotate credentials** regularly
6. **Enable MFA** for AWS Console access

## Next Steps

After successful deployment:

1. Configure custom domain
2. Set up CI/CD pipeline
3. Add monitoring dashboards
4. Configure backup strategy
5. Set up alerting
6. Perform security audit
7. Load testing

## Support

For deployment issues:
- Check CloudFormation events
- Review Lambda logs in CloudWatch
- Verify IAM permissions
- Contact AWS Support if needed
