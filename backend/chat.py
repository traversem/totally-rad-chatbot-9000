"""
Chat Lambda Handler - Handles chat requests and interacts with AWS Bedrock
"""
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field, ValidationError

# Initialize AWS services
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('REGION', 'eu-west-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'eu-west-1'))
table = dynamodb.Table(os.environ['CHAT_HISTORY_TABLE'])

# Initialize Powertools
logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()


class ChatMessage(BaseModel):
    """Chat message request model"""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: str | None = None
    system_prompt: str | None = Field(default=None, max_length=5000)


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    conversation_id: str
    timestamp: str


@tracer.capture_method
def invoke_bedrock(message: str, system_prompt: str | None = None) -> str:
    """
    Invoke AWS Bedrock with Claude model

    Args:
        message: User's message
        system_prompt: Optional system prompt to set context

    Returns:
        AI response text
    """
    model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')

    # Build messages for Claude
    messages = [
        {
            "role": "user",
            "content": message
        }
    ]

    # Prepare the request body
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.9
    }

    # Add system prompt if provided
    if system_prompt:
        request_body["system"] = system_prompt

    logger.info(f"Invoking Bedrock model: {model_id}")

    try:
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )

        # Parse response
        response_body = json.loads(response['body'].read())

        # Extract the text from Claude's response
        if 'content' in response_body and len(response_body['content']) > 0:
            return response_body['content'][0]['text']
        else:
            raise ValueError("Unexpected response format from Bedrock")

    except Exception as e:
        logger.error(f"Error invoking Bedrock: {str(e)}")
        raise


@tracer.capture_method
def save_to_history(user_id: str, conversation_id: str, user_message: str, ai_response: str) -> None:
    """
    Save chat interaction to DynamoDB

    Args:
        user_id: User's Cognito ID
        conversation_id: Conversation UUID
        user_message: User's message
        ai_response: AI's response
    """
    timestamp = int(datetime.utcnow().timestamp() * 1000)

    try:
        table.put_item(
            Item={
                'userId': user_id,
                'conversationId': conversation_id,
                'timestamp': timestamp,
                'userMessage': user_message,
                'aiResponse': ai_response,
                'createdAt': datetime.utcnow().isoformat()
            }
        )
        logger.info(f"Saved conversation {conversation_id} to history")
    except Exception as e:
        logger.error(f"Error saving to DynamoDB: {str(e)}")
        # Don't fail the request if history save fails
        pass


@app.post("/chat")
@tracer.capture_method
def chat_handler() -> Dict[str, Any]:
    """
    Handle chat POST requests

    Returns:
        API Gateway response with AI response
    """
    try:
        # Get user ID from Cognito claims
        claims = app.current_event.request_context.authorizer.claims
        user_id = claims.get('sub', 'unknown')

        # Parse and validate request
        try:
            body = json.loads(app.current_event.body)
            chat_request = ChatMessage(**body)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(f"Invalid request: {str(e)}")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid request format"})
            }

        # Generate or use existing conversation ID
        conversation_id = chat_request.conversation_id or str(uuid.uuid4())

        # Get AI response from Bedrock
        ai_response = invoke_bedrock(
            message=chat_request.message,
            system_prompt=chat_request.system_prompt
        )

        # Save to history (async, don't block response)
        save_to_history(
            user_id=user_id,
            conversation_id=conversation_id,
            user_message=chat_request.message,
            ai_response=ai_response
        )

        # Return response
        response = ChatResponse(
            response=ai_response,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow().isoformat()
        )

        return {
            "statusCode": 200,
            "body": response.model_dump_json()
        }

    except Exception as e:
        logger.exception("Error processing chat request")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler entry point

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        API Gateway response
    """
    return app.resolve(event, context)
