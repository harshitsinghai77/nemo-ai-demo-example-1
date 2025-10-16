import uuid
from http import HTTPStatus
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from pydantic import ValidationError

from schemas import ImageAnalysisRequest
from storage import save_analysis, get_analysis
from image_analyzer import analyze_image, generate_summary, detect_moderation_labels

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()

@app.post("/images")
def create_image_analysis():
    try:
        body = app.current_event.json_body
        request = ImageAnalysisRequest(**body)
    except ValidationError as e:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": f"Validation error: {str(e)}"}
    except TypeError as e:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": f"Type error: {str(e)}"}

    analysis_id = str(uuid.uuid4())
    labels = analyze_image(request.bucket, request.key)
    summary = generate_summary(labels)
    moderation_labels = detect_moderation_labels(request.bucket, request.key)

    save_analysis(analysis_id, labels, summary, moderation_labels)

    return {"analysis_id": analysis_id}

@app.get("/images/<analysis_id>")
def get_image_analysis(analysis_id: str):
    analysis = get_analysis(analysis_id)
    if not analysis:
        return {"statusCode": HTTPStatus.NOT_FOUND, "body": "Analysis not found"}
    return analysis

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)