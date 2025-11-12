#!/bin/bash
set -e

# Totally Rad Chatbot 9000 Deployment Script
# This script deploys the entire application to AWS

echo "🚀 Deploying Totally Rad Chatbot 9000..."

# Configuration
STACK_NAME="totally-rad-chatbot-9000"
REGION="eu-west-1"
PROFILE="emea-sandbox03"
S3_BUCKET="${STACK_NAME}-artifacts-${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --profile $PROFILE --query Account --output text)}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Installing backend dependencies...${NC}"
pip install -r backend/requirements.txt -t backend/ --upgrade

echo -e "${BLUE}Step 2: Creating S3 bucket for SAM artifacts...${NC}"
aws s3 mb s3://${S3_BUCKET} --region ${REGION} --profile ${PROFILE} 2>/dev/null || echo "Bucket already exists"

echo -e "${BLUE}Step 3: Building and deploying SAM application...${NC}"
sam build --profile ${PROFILE}

sam deploy \
  --stack-name ${STACK_NAME} \
  --s3-bucket ${S3_BUCKET} \
  --capabilities CAPABILITY_IAM \
  --region ${REGION} \
  --profile ${PROFILE} \
  --no-fail-on-empty-changeset \
  --parameter-overrides Environment=prod

echo -e "${BLUE}Step 4: Getting stack outputs...${NC}"
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_NAME} \
  --region ${REGION} \
  --profile ${PROFILE} \
  --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
  --output text)

USER_POOL_ID=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_NAME} \
  --region ${REGION} \
  --profile ${PROFILE} \
  --query "Stacks[0].Outputs[?OutputKey=='UserPoolId'].OutputValue" \
  --output text)

USER_POOL_CLIENT_ID=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_NAME} \
  --region ${REGION} \
  --profile ${PROFILE} \
  --query "Stacks[0].Outputs[?OutputKey=='UserPoolClientId'].OutputValue" \
  --output text)

FRONTEND_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_NAME} \
  --region ${REGION} \
  --profile ${PROFILE} \
  --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
  --output text)

FRONTEND_URL=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_NAME} \
  --region ${REGION} \
  --profile ${PROFILE} \
  --query "Stacks[0].Outputs[?OutputKey=='FrontendUrl'].OutputValue" \
  --output text)

echo -e "${BLUE}Step 5: Building frontend with environment variables...${NC}"
cd frontend

# Create .env file for build
cat > .env << EOF
VITE_API_ENDPOINT=${API_ENDPOINT}
VITE_USER_POOL_ID=${USER_POOL_ID}
VITE_USER_POOL_CLIENT_ID=${USER_POOL_CLIENT_ID}
VITE_REGION=${REGION}
EOF

npm run build

echo -e "${BLUE}Step 6: Deploying frontend to S3...${NC}"
aws s3 sync dist/ s3://${FRONTEND_BUCKET}/ \
  --region ${REGION} \
  --profile ${PROFILE} \
  --delete

echo -e "${BLUE}Step 7: Invalidating CloudFront cache...${NC}"
DISTRIBUTION_ID=$(aws cloudfront list-distributions \
  --profile ${PROFILE} \
  --query "DistributionList.Items[?Origins.Items[?DomainName=='${FRONTEND_BUCKET}.s3.${REGION}.amazonaws.com']].Id" \
  --output text)

if [ ! -z "$DISTRIBUTION_ID" ]; then
  aws cloudfront create-invalidation \
    --distribution-id ${DISTRIBUTION_ID} \
    --paths "/*" \
    --profile ${PROFILE} \
    --no-cli-pager
fi

cd ..

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 Totally Rad Chatbot 9000 is LIVE!${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Frontend URL:    ${BLUE}${FRONTEND_URL}${NC}"
echo -e "API Endpoint:    ${BLUE}${API_ENDPOINT}${NC}"
echo -e "User Pool ID:    ${BLUE}${USER_POOL_ID}${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Visit the frontend URL to access the chatbot"
echo "2. Sign up for a new account"
echo "3. Verify your email address"
echo "4. Start chatting with Claude!"
echo ""
