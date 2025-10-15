import boto3
import json
from typing import List, Dict, Any
from aws_lambda_powertools import Logger, Tracer
from botocore.exceptions import ClientError

logger = Logger()
tracer = Tracer()

rekognition = boto3.client("rekognition")
bedrock = boto3.client("bedrock-runtime")

@tracer.capture_method
def analyze_image(bucket: str, key: str):
    logger.info(f"Analyzing image {key} from bucket {bucket}")
    response = rekognition.detect_labels(
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
        MaxLabels=10,
    )
    return response["Labels"]

@tracer.capture_method
def detect_moderation_content(bucket: str, key: str) -> List[Dict[str, Any]]:
    logger.info(f"Detecting moderation content for image {key} from bucket {bucket}")
    try:
        response = rekognition.detect_moderation_labels(
            Image={"S3Object": {"Bucket": bucket, "Name": key}},
            MinConfidence=60
        )
        return response.get("ModerationLabels", [])
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS ClientError detecting moderation content: {error_code} - {error_message}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error detecting moderation content: {type(e).__name__} - {str(e)}")
        return []

@tracer.capture_method
def generate_summary(labels: list) -> str:
    logger.info("Generating summary for labels")
    prompt = f"Create a short, descriptive summary for an image containing the following elements: {', '.join([label['Name'] for label in labels])}."

    response = bedrock.invoke_model(
        body=json.dumps({
            "prompt": f"\n\nHuman:{prompt}\n\nAssistant:",
            "max_tokens_to_sample": 300,
            "temperature": 0.7,
            "top_p": 0.9,
        }),
        modelId="anthropic.claude-v2",
        contentType="application/json",
        accept="application/json",
    )

    result = json.loads(response['body'].read())
    return result['completion']