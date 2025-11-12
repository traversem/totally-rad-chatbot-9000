"""
History Lambda Handler - Retrieves chat history for users
"""
import json
import os
from typing import Any, Dict

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3.dynamodb.conditions import Key

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'eu-west-1'))
table = dynamodb.Table(os.environ['CHAT_HISTORY_TABLE'])

# Initialize Powertools
logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()


@app.get("/history")
@tracer.capture_method
def get_history_handler() -> Dict[str, Any]:
    """
    Get chat history for authenticated user

    Query parameters:
        - conversation_id: Optional, filter by specific conversation
        - limit: Optional, max number of items to return (default: 50)

    Returns:
        API Gateway response with chat history
    """
    try:
        # Get user ID from Cognito claims
        claims = app.current_event.request_context.authorizer.claims
        user_id = claims.get('sub', 'unknown')

        # Get query parameters
        query_params = app.current_event.query_string_parameters or {}
        conversation_id = query_params.get('conversation_id')
        limit = int(query_params.get('limit', 50))

        # Validate limit
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1

        logger.info(f"Fetching history for user: {user_id}, conversation: {conversation_id}")

        # Query DynamoDB
        if conversation_id:
            # Get specific conversation
            response = table.query(
                KeyConditionExpression=Key('userId').eq(user_id) & Key('conversationId').eq(conversation_id),
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
        else:
            # Get all conversations for user
            response = table.query(
                KeyConditionExpression=Key('userId').eq(user_id),
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )

        items = response.get('Items', [])

        return {
            "statusCode": 200,
            "body": json.dumps({
                "history": items,
                "count": len(items)
            }, default=str)
        }

    except ValueError as e:
        logger.warning(f"Invalid parameters: {str(e)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid query parameters"})
        }
    except Exception as e:
        logger.exception("Error retrieving history")
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
