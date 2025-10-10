from typing import List, Dict, Any
import boto3
import json
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()

rekognition = boto3.client("rekognition")
bedrock = boto3.client("bedrock-runtime")

# Constants
DEFAULT_MODERATION_CONFIDENCE_THRESHOLD = 50.0

@tracer.capture_method
def analyze_image(bucket: str, key: str):
    logger.info(f"Analyzing image {key} from bucket {bucket}")
    response = rekognition.detect_labels(
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
        MaxLabels=10,
    )
    return response["Labels"]

@tracer.capture_method
def detect_moderation_labels(bucket: str, key: str) -> List[Dict[str, Any]]:
    """
    Detects inappropriate, unwanted, or offensive content in an image using AWS Rekognition.
    
    This function analyzes an image stored in S3 to identify potentially sensitive content
    such as explicit nudity, violence, hate symbols, drugs, and other inappropriate material.
    
    Args:
        bucket (str): The S3 bucket name containing the image
        key (str): The S3 key/path of the image to analyze
        
    Returns:
        list: A list of moderation labels detected in the image. Each label contains:
            - Name: The type of inappropriate content detected
            - Confidence: Confidence score (0-100) for the detection
            - ParentName: The parent category of the label
            - TaxonomyLevel: The hierarchy level (1-3) of the label
            Returns empty list if no moderation issues found or if detection fails.
    """
    logger.info(f"Detecting moderation labels for image {key} from bucket {bucket}")
    try:
        response = rekognition.detect_moderation_labels(
            Image={"S3Object": {"Bucket": bucket, "Name": key}},
            MinConfidence=DEFAULT_MODERATION_CONFIDENCE_THRESHOLD
        )
        moderation_labels = response.get("ModerationLabels", [])
        logger.info(f"Found {len(moderation_labels)} moderation labels")
        return moderation_labels
    except Exception as e:
        logger.error(f"Error detecting moderation labels: {str(e)}")
        # Return empty list if moderation detection fails to maintain service availability
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