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
    logger.info(f"Analyzing image {key} from bucket {bucket}")
    response = rekognition.detect_labels(
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
        MaxLabels=10,
    )
    return response["Labels"]

@tracer.capture_method
def detect_moderation_content(bucket: str, key: str) -> List[Dict[str, Any]]:
    """
    Detects inappropriate or sensitive content in an image using Amazon Rekognition.
    
    Args:
        bucket (str): S3 bucket name containing the image
        key (str): S3 object key for the image
        
    Returns:
        List[Dict[str, Any]]: List of moderation labels detected in the image,
                              empty list if no issues found or on error
    """
    logger.info(f"Analyzing moderation content for image {key} from bucket {bucket}")
    try:
        response = rekognition.detect_moderation_labels(
            Image={"S3Object": {"Bucket": bucket, "Name": key}},
            MinConfidence=50.0,
        )
        moderation_labels = response.get("ModerationLabels", [])
        logger.info(f"Found {len(moderation_labels)} moderation labels for image {key}")
        return moderation_labels
    except rekognition.exceptions.InvalidS3ObjectException:
        logger.error(f"Invalid S3 object: bucket={bucket}, key={key}")
        return []
    except rekognition.exceptions.InvalidImageFormatException:
        logger.error(f"Invalid image format for object: bucket={bucket}, key={key}")
        return []
    except rekognition.exceptions.ImageTooLargeException:
        logger.error(f"Image too large for processing: bucket={bucket}, key={key}")
        return []
    except rekognition.exceptions.AccessDeniedException:
        logger.error(f"Access denied to Rekognition service for bucket={bucket}, key={key}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error detecting moderation content for {key}: {str(e)}", exc_info=True)
        # Return empty list if moderation detection fails to not break the main workflow
        return []

@tracer.capture_method
def generate_summary(labels: List[Dict[str, Any]]) -> str:
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