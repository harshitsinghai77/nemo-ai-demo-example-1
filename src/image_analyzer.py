import boto3
import json
from typing import List, Dict, Any
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()

rekognition = boto3.client("rekognition")
bedrock = boto3.client("bedrock-runtime")

@tracer.capture_method
def analyze_image(bucket: str, key: str) -> List[Dict[str, Any]]:
    """
    Analyze an image in an S3 bucket and return a list of detected labels.
    
    Args:
        bucket (str): The S3 bucket name.
        key (str): The S3 object key.
    
    Returns:
        List[Dict[str, Any]]: A list of detected labels.
    """
    logger.info(f"Analyzing image {key} from bucket {bucket}")
    response = rekognition.detect_labels(
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
        MaxLabels=10,
    )
    return response["Labels"]

@tracer.capture_method
def detect_moderation_labels(bucket: str, key: str) -> List[Dict[str, Any]]:
    """
    Detect moderation labels for potentially inappropriate content in an image.
    
    Args:
        bucket (str): The S3 bucket name.
        key (str): The S3 object key.
    
    Returns:
        List[Dict[str, Any]]: A list of moderation labels indicating potentially 
                              sensitive or inappropriate content. Empty if no issues detected.
    """
    logger.info(f"Detecting moderation labels for image {key} from bucket {bucket}")
    try:
        response = rekognition.detect_moderation_labels(
            Image={"S3Object": {"Bucket": bucket, "Name": key}},
            MinConfidence=50.0
        )
        return response.get("ModerationLabels", [])
    except Exception as e:
        logger.error(f"Error detecting moderation labels: {str(e)}")
        return []

@tracer.capture_method
def generate_summary(labels: List[Dict[str, Any]]) -> str:
    """
    Generate a descriptive summary of an image based on detected labels.
    
    Args:
        labels (List[Dict[str, Any]]): A list of detected labels from image analysis.
    
    Returns:
        str: A human-readable summary of the image content.
    """
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