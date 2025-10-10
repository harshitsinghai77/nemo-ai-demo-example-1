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
    Detects inappropriate or sensitive content in an image using AWS Rekognition.
    
    Args:
        bucket (str): The S3 bucket name containing the image
        key (str): The S3 key/path of the image to analyze
        
    Returns:
        List[Dict[str, Any]]: A list of moderation labels with confidence scores,
                             or empty list if no inappropriate content is detected
                             or if the analysis fails
    """
    logger.info(f"Detecting moderation labels for image {key} from bucket {bucket}")
    logger.info("Using minimum confidence threshold of 60.0 for moderation detection")
    try:
        response = rekognition.detect_moderation_labels(
            Image={"S3Object": {"Bucket": bucket, "Name": key}},
            MinConfidence=60.0,
        )
        return response.get("ModerationLabels", [])
    except Exception as e:
        logger.error(f"Failed to detect moderation labels: {str(e)}")
        # Return empty list if moderation fails - this ensures the main analysis continues
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