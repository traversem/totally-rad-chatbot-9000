"""
Health Check Lambda Handler - Simple health check endpoint
"""
import json
from datetime import datetime
from typing import Any, Dict

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

# Initialize Powertools
logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()


@app.get("/health")
@tracer.capture_method
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint - no authentication required

    Returns:
        API Gateway response with health status
    """
    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "healthy",
            "service": "totally-rad-chatbot-9000",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        })
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
