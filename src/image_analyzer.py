import boto3
import json
from aws_lambda_powertools import Logger, Tracer
from typing import List, Dict, Any, Optional

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
def detect_moderation_labels(bucket: str, key: str) -> Optional[List[Dict[str, Any]]]:
    """
    Detect inappropriate or sensitive content in an image using AWS Rekognition.
    
    Args:
        bucket (str): S3 bucket name where the image is stored
        key (str): S3 key of the image to analyze
        
    Returns:
        Optional[List[Dict[str, Any]]]: List of moderation labels if any are found, 
                                       None if no moderation issues detected
    """
    try:
        logger.info(f"Detecting moderation labels for image {key} from bucket {bucket}")
        response = rekognition.detect_moderation_labels(
            Image={"S3Object": {"Bucket": bucket, "Name": key}},
            MinConfidence=60.0,  # Set minimum confidence threshold
        )
        
        moderation_labels = response.get("ModerationLabels", [])
        
        if moderation_labels:
            logger.info(f"Found {len(moderation_labels)} moderation labels for image {key}")
            return moderation_labels
        else:
            logger.info(f"No moderation issues detected for image {key}")
            return None
            
    except Exception as e:
        logger.error(f"Error detecting moderation labels for image {key}: {str(e)}")
        # Return None if moderation detection fails, so the main analysis can continue
        return None

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