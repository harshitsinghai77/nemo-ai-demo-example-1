import boto3
import json
from aws_lambda_powertools import Logger, Tracer

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
def detect_moderation_labels(bucket: str, key: str):
    """
    Detects inappropriate, unwanted, or offensive content in an image.
    Returns a list of moderation labels or empty list if no issues detected.
    """
    logger.info(f"Detecting moderation labels for image {key} from bucket {bucket}")
    
    try:
        response = rekognition.detect_moderation_labels(
            Image={"S3Object": {"Bucket": bucket, "Name": key}},
            MinConfidence=50.0  # Default confidence threshold
        )
        
        moderation_labels = response.get("ModerationLabels", [])
        logger.info(f"Found {len(moderation_labels)} moderation labels")
        
        return moderation_labels
    
    except Exception as e:
        logger.error(f"Error detecting moderation labels: {str(e)}")
        # Return empty list on error to maintain consistent response format
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