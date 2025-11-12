# Totally Rad Chatbot 9000 🎮

> The most excellent AI-powered chatbot experience, powered by Claude on AWS Bedrock

A production-ready, secure, and beautifully designed chatbot application that showcases the power of AWS Bedrock, serverless architecture, and 90s-inspired aesthetics.

## 🌟 Features

- **🤖 AI-Powered**: Uses Claude (Anthropic) via AWS Bedrock for intelligent conversations
- **🔒 Secure by Design**: AWS Cognito authentication with MFA support, encrypted data at rest
- **⚡ Serverless Architecture**: Fully serverless using AWS Lambda, API Gateway, and S3
- **📱 Responsive Design**: Beautiful retro 90s-inspired UI that works on all devices
- **💾 Chat History**: Persistent conversation storage in DynamoDB
- **🚀 One-Command Deploy**: Automated deployment with zero manual configuration
- **💰 Cost-Optimized**: Pay-per-request pricing with no idle costs
- **📊 Observable**: Built-in logging and tracing with AWS Lambda Powertools

## 🏗️ Architecture

```
┌─────────────┐
│   CloudFront│  ← CDN for frontend
└──────┬──────┘
       │
┌──────▼──────┐
│  S3 Bucket  │  ← Static website hosting
└─────────────┘

┌─────────────┐
│  API Gateway│  ← REST API endpoint
└──────┬──────┘
       │
┌──────▼──────┐
│   Lambda    │  ← Python functions
└──────┬──────┘
       │
       ├─────────► AWS Bedrock (Claude)
       │
       └─────────► DynamoDB (Chat history)

┌─────────────┐
│AWS Cognito  │  ← User authentication
└─────────────┘
```

### Tech Stack

**Frontend:**
- Vue 3 with TypeScript
- Vite for blazing-fast builds
- AWS Amplify for Cognito integration
- Axios for API calls

**Backend:**
- Python 3.12
- AWS Lambda with Powertools
- Pydantic for data validation
- boto3 for AWS SDK

**Infrastructure:**
- AWS CloudFormation (via SAM)
- AWS Lambda
- API Gateway
- Cognito
- DynamoDB
- S3 + CloudFront
- AWS Bedrock

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with `emea-sandbox03` profile
- Node.js 18+ and npm
- Python 3.12+
- AWS SAM CLI
- Access to AWS Bedrock models in `eu-west-1`

### One-Command Deployment

```bash
./deploy.sh
```

That's it! The script will:
1. Install backend dependencies
2. Build and deploy the SAM application
3. Create all AWS resources (Lambda, API Gateway, Cognito, DynamoDB, S3, CloudFront)
4. Build the frontend with correct environment variables
5. Deploy frontend to S3
6. Configure CloudFront distribution
7. Output the live URLs

Deployment takes approximately 5-10 minutes.

### Manual Deployment Steps

If you prefer to deploy manually:

```bash
# 1. Install backend dependencies
pip install -r backend/requirements.txt -t backend/ --upgrade

# 2. Create S3 bucket for artifacts
aws s3 mb s3://totally-rad-chatbot-9000-artifacts --region eu-west-1 --profile emea-sandbox03

# 3. Build and deploy SAM
sam build --profile emea-sandbox03
sam deploy --stack-name totally-rad-chatbot-9000 \
  --s3-bucket totally-rad-chatbot-9000-artifacts \
  --capabilities CAPABILITY_IAM \
  --region eu-west-1 \
  --profile emea-sandbox03

# 4. Get stack outputs
aws cloudformation describe-stacks \
  --stack-name totally-rad-chatbot-9000 \
  --region eu-west-1 \
  --profile emea-sandbox03 \
  --query "Stacks[0].Outputs"

# 5. Build frontend (replace with actual values from step 4)
cd frontend
cat > .env << EOF
VITE_API_ENDPOINT=<API_ENDPOINT>
VITE_USER_POOL_ID=<USER_POOL_ID>
VITE_USER_POOL_CLIENT_ID=<USER_POOL_CLIENT_ID>
VITE_REGION=eu-west-1
EOF
npm run build

# 6. Deploy to S3
aws s3 sync dist/ s3://<FRONTEND_BUCKET>/ --region eu-west-1 --profile emea-sandbox03 --delete

# 7. Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id <DISTRIBUTION_ID> --paths "/*" --profile emea-sandbox03
```

## 📖 Usage

### Sign Up

1. Navigate to the frontend URL (output after deployment)
2. Click "Don't have an account? Sign Up"
3. Enter your email and a strong password (min 8 chars, uppercase, lowercase, number, symbol)
4. Check your email for a verification code
5. Enter the verification code to confirm your account

### Sign In

1. Enter your email and password
2. Click "Sign In"
3. You're ready to chat!

### Chatting

- Type your message in the input box
- Press Enter to send (Shift+Enter for new line)
- Click suggested prompts for inspiration
- Your chat history is automatically saved

### Sign Out

Click the "Sign Out" button in the top right corner.

## 🔒 Security Features

- ✅ **Authentication**: AWS Cognito with email verification
- ✅ **Authorization**: JWT tokens for API access
- ✅ **MFA Support**: Optional software token MFA
- ✅ **Advanced Security Mode**: Cognito advanced security for anomaly detection
- ✅ **Encryption at Rest**: All data encrypted in DynamoDB and S3
- ✅ **Encryption in Transit**: HTTPS everywhere (CloudFront + API Gateway)
- ✅ **Least Privilege**: IAM roles with minimal required permissions
- ✅ **No Public S3**: S3 bucket not publicly accessible, served via CloudFront OAC
- ✅ **CORS Protection**: API Gateway CORS properly configured
- ✅ **Input Validation**: Pydantic models for request validation
- ✅ **XSS Protection**: Vue.js automatic escaping

## 💰 Cost Optimization

The application is designed to minimize costs:

- **Serverless**: Pay only for what you use
- **DynamoDB on-demand**: No idle costs
- **CloudFront**: Efficient CDN with caching
- **Lambda ARM**: x86_64 architecture (configurable to ARM for 20% savings)
- **Claude Haiku**: Using cost-effective Claude Haiku model (configurable)
- **API Gateway HTTP**: Could use HTTP API for 70% savings (currently using REST for features)

**Estimated monthly cost** (for moderate usage):
- Lambda: $1-5
- API Gateway: $3-10
- DynamoDB: $1-5
- S3 + CloudFront: $1-2
- Cognito: Free tier (50,000 MAUs)
- **Total: ~$10-25/month** for hundreds of users

## 🧪 Testing

### Test the API

```bash
# Health check (no auth required)
curl https://YOUR_API_ENDPOINT/health

# Get chat history (requires auth)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://YOUR_API_ENDPOINT/history

# Send a message (requires auth)
curl -X POST \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}' \
  https://YOUR_API_ENDPOINT/chat
```

## 🛠️ Development

### Local Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:5173`

Note: You'll need to deploy the backend first to have API endpoints.

### Project Structure

```
totally-rad-chatbot-9000/
├── backend/              # Python Lambda functions
│   ├── chat.py          # Chat handler
│   ├── history.py       # History handler
│   ├── health.py        # Health check
│   └── requirements.txt
├── frontend/            # Vue 3 TypeScript app
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── services/    # API and auth services
│   │   ├── App.vue      # Main app component
│   │   └── config.ts    # Configuration
│   └── package.json
├── template.yaml        # SAM/CloudFormation template
├── deploy.sh           # Deployment script
├── README.md           # This file
└── WHY_CHOOSE_ME.md    # Competition submission
```

## 🔧 Configuration

### Change Bedrock Model

Edit `template.yaml`:

```yaml
Environment:
  Variables:
    BEDROCK_MODEL_ID: anthropic.claude-3-sonnet-20240229-v1:0  # or any other model
```

### Enable Lambda ARM Architecture

Edit `template.yaml`:

```yaml
Architectures:
  - arm64  # Change from x86_64
```

### Adjust Lambda Resources

Edit `template.yaml`:

```yaml
Timeout: 30      # Increase for longer responses
MemorySize: 512  # Increase for better performance
```

## 📊 Monitoring

### CloudWatch Logs

View logs for each Lambda function:

```bash
aws logs tail /aws/lambda/totally-rad-chatbot-9000-ChatFunction --follow --profile emea-sandbox03
aws logs tail /aws/lambda/totally-rad-chatbot-9000-GetHistoryFunction --follow --profile emea-sandbox03
aws logs tail /aws/lambda/totally-rad-chatbot-9000-HealthCheckFunction --follow --profile emea-sandbox03
```

### X-Ray Tracing

The application uses AWS Lambda Powertools for distributed tracing. View traces in the AWS X-Ray console.

### CloudWatch Metrics

Monitor:
- Lambda invocations and errors
- API Gateway requests and latency
- DynamoDB read/write capacity
- Cognito authentication attempts

## 🧹 Cleanup

To remove all AWS resources:

```bash
# Delete the CloudFormation stack
aws cloudformation delete-stack \
  --stack-name totally-rad-chatbot-9000 \
  --region eu-west-1 \
  --profile emea-sandbox03

# Empty and delete S3 buckets (they won't auto-delete if not empty)
aws s3 rm s3://totally-rad-chatbot-9000-frontend-ACCOUNT_ID --recursive --profile emea-sandbox03
aws s3 rb s3://totally-rad-chatbot-9000-frontend-ACCOUNT_ID --profile emea-sandbox03

aws s3 rm s3://totally-rad-chatbot-9000-artifacts-ACCOUNT_ID --recursive --profile emea-sandbox03
aws s3 rb s3://totally-rad-chatbot-9000-artifacts-ACCOUNT_ID --profile emea-sandbox03
```

## 🐛 Troubleshooting

### Frontend shows "Network Error"

- Check API endpoint in browser console
- Verify API Gateway is deployed
- Check CORS configuration
- Ensure you're authenticated (valid JWT token)

### "User is not authenticated"

- Sign out and sign in again
- Clear browser local storage
- Check Cognito user pool configuration

### "Access Denied" errors

- Check IAM role permissions in CloudFormation
- Verify Lambda execution role has Bedrock access
- Check DynamoDB table permissions

### Bedrock InvokeModel fails

- Verify you have access to the Bedrock model in `eu-west-1`
- Check AWS account has Bedrock enabled
- Try a different model ID

## 📝 License

This project was created for the AI Coding Assistant Battle Royale competition.

## 🎯 Next Steps

See `WHY_CHOOSE_ME.md` for roadmap and future enhancements.

---

Built with ❤️ and lots of 90s nostalgia by Claude
