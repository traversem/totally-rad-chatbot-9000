# Deployment Guide

## Quick Start

The simplest way to deploy is using the provided deployment script:

```bash
cd /workspace/totally-rad-chatbot-9000
./deploy.sh
```

## Manual Deployment Steps

If you prefer manual deployment or the script fails, follow these steps:

### Prerequisites

- AWS CLI configured with `emea-sandbox03` profile
- Docker running (required for SAM build)
- Node.js 18+ and npm
- AWS SAM CLI

### Step-by-Step Deployment

#### 1. Navigate to Project Root

```bash
cd /workspace/totally-rad-chatbot-9000
```

**IMPORTANT**: All commands must be run from the project root directory, not from subdirectories.

#### 2. Build the SAM Application

```bash
sam build --use-container
```

This will:
- Build Lambda functions in Docker containers
- Package Python dependencies
- Prepare deployment artifacts

**Note**: The `--use-container` flag is required because the build environment doesn't have pip installed.

#### 3. Create S3 Bucket for Artifacts

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --profile emea-sandbox03 --query Account --output text)
aws s3 mb s3://totally-rad-chatbot-9000-artifacts-${ACCOUNT_ID} \
  --region eu-west-1 \
  --profile emea-sandbox03
```

#### 4. Deploy SAM Stack

```bash
sam deploy \
  --stack-name totally-rad-chatbot-9000 \
  --s3-bucket totally-rad-chatbot-9000-artifacts-${ACCOUNT_ID} \
  --capabilities CAPABILITY_IAM \
  --region eu-west-1 \
  --profile emea-sandbox03 \
  --parameter-overrides Environment=prod
```

This creates:
- 3 Lambda functions (Chat, History, Health Check)
- API Gateway REST API
- Cognito User Pool
- DynamoDB table
- S3 bucket + CloudFront distribution
- IAM roles and policies

**Deployment time**: ~5-10 minutes (CloudFront takes the longest)

#### 5. Get Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name totally-rad-chatbot-9000 \
  --region eu-west-1 \
  --profile emea-sandbox03 \
  --query "Stacks[0].Outputs"
```

Save these values - you'll need them for the frontend:
- `ApiEndpoint`
- `UserPoolId`
- `UserPoolClientId`
- `FrontendBucketName`
- `FrontendUrl`

#### 6. Build Frontend

```bash
cd frontend

# Create .env file with stack outputs from step 5
cat > .env << EOF
VITE_API_ENDPOINT=<ApiEndpoint from step 5>
VITE_USER_POOL_ID=<UserPoolId from step 5>
VITE_USER_POOL_CLIENT_ID=<UserPoolClientId from step 5>
VITE_REGION=eu-west-1
EOF

# Install dependencies (if not already done)
npm install

# Build for production
npm run build
```

#### 7. Deploy Frontend to S3

```bash
aws s3 sync dist/ s3://<FrontendBucketName>/ \
  --region eu-west-1 \
  --profile emea-sandbox03 \
  --delete
```

#### 8. Invalidate CloudFront Cache

```bash
# Get CloudFront distribution ID
DISTRIBUTION_ID=$(aws cloudfront list-distributions \
  --profile emea-sandbox03 \
  --query "DistributionList.Items[?contains(Origins.Items[0].DomainName, '<FrontendBucketName>')].Id" \
  --output text)

# Create invalidation
aws cloudfront create-invalidation \
  --distribution-id ${DISTRIBUTION_ID} \
  --paths "/*" \
  --profile emea-sandbox03
```

#### 9. Access Your Application

Visit the `FrontendUrl` from step 5 in your browser.

## Troubleshooting

### SAM Build Fails with "requirements.txt not found"

**Cause**: SAM is running from the wrong directory.

**Solution**: Make sure you're in the project root (`/workspace/totally-rad-chatbot-9000`), not in the `frontend/` or `backend/` directory.

### SAM Build Fails with "python not found" or "pip not found"

**Cause**: Build environment doesn't have Python/pip installed.

**Solution**: Use the `--use-container` flag:
```bash
sam build --use-container
```

### Lambda Functions Fail to Create with "Empty ZIP" Error

**Cause**: SAM build didn't copy Python files to the build directory.

**Solution**:
1. Delete the build directory: `rm -rf .aws-sam`
2. Make sure you're in the project root
3. Rebuild: `sam build --use-container`
4. Verify files exist: `ls -la .aws-sam/build/ChatFunction/`

### CloudFront Takes Too Long

**Cause**: CloudFront distributions take 5-15 minutes to deploy.

**Solution**: This is normal. CloudFront is deploying to edge locations worldwide. You can check status:
```bash
aws cloudfront get-distribution \
  --id ${DISTRIBUTION_ID} \
  --profile emea-sandbox03 \
  --query "Distribution.Status"
```

### Frontend Shows "Network Error"

**Possible causes**:
1. API endpoint not configured correctly in `.env`
2. API Gateway not deployed
3. CORS issues

**Solutions**:
1. Verify API endpoint in browser console
2. Test API health check:
   ```bash
   curl https://<API_ENDPOINT>/prod/health
   ```
3. Check CORS configuration in template.yaml

### "User Not Authenticated" Errors

**Possible causes**:
1. Cognito configuration mismatch
2. JWT token expired
3. User Pool ID or Client ID incorrect

**Solutions**:
1. Verify Cognito configuration in `.env`
2. Sign out and sign in again
3. Clear browser local storage

## Deployment Architecture

```
GitHub Repo
    │
    ├─> GitHub Actions (CI/CD)
    │
    ├─> SAM Build (Docker)
    │   └─> Lambda Functions (Python 3.9)
    │
    ├─> CloudFormation
    │   ├─> API Gateway
    │   ├─> Lambda
    │   ├─> Cognito
    │   ├─> DynamoDB
    │   ├─> S3
    │   └─> CloudFront
    │
    └─> Frontend Build (Vite)
        └─> S3 + CloudFront
```

## Cost Estimate

**Monthly cost for moderate usage** (~100 users, ~1000 requests/day):

- **Lambda**: $2-5 (1M free tier requests)
- **API Gateway**: $3-10 (1M free tier requests first year)
- **DynamoDB**: $1-5 (25GB free tier)
- **S3**: $0.50-1
- **CloudFront**: $1-2 (1TB free tier first year)
- **Cognito**: Free (50,000 MAU)

**Total**: ~$10-25/month

## Cleanup

To remove all resources and avoid costs:

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack \
  --stack-name totally-rad-chatbot-9000 \
  --region eu-west-1 \
  --profile emea-sandbox03

# Empty and delete S3 buckets (not auto-deleted)
ACCOUNT_ID=$(aws sts get-caller-identity --profile emea-sandbox03 --query Account --output text)

aws s3 rm s3://totally-rad-chatbot-9000-frontend-${ACCOUNT_ID} --recursive --profile emea-sandbox03
aws s3 rb s3://totally-rad-chatbot-9000-frontend-${ACCOUNT_ID} --profile emea-sandbox03

aws s3 rm s3://totally-rad-chatbot-9000-artifacts-${ACCOUNT_ID} --recursive --profile emea-sandbox03
aws s3 rb s3://totally-rad-chatbot-9000-artifacts-${ACCOUNT_ID} --profile emea-sandbox03
```

## Security Notes

- All data is encrypted at rest (DynamoDB, S3)
- All traffic is HTTPS only
- S3 bucket is not publicly accessible
- API requires authentication (except /health)
- Cognito enforces strong password policy
- IAM roles follow least privilege principle

## Next Steps

After successful deployment:

1. **Create an account**: Sign up at the frontend URL
2. **Verify your email**: Check your inbox for verification code
3. **Start chatting**: Log in and start a conversation with Claude!
4. **Monitor costs**: Set up billing alerts in AWS Console
5. **Review logs**: Check CloudWatch for Lambda execution logs

---

For issues or questions, see the main README.md or open an issue on GitHub.
