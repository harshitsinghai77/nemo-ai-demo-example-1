import os
import boto3
from aws_lambda_powertools import Logger, Tracer
from typing import List, Dict, Any, Optional

logger = Logger()
tracer = Tracer()

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ.get("DDB_TABLE_NAME", ""))

@tracer.capture_method
def save_analysis(analysis_id: str, labels: list, summary: str, moderation: Optional[List[Dict[str, Any]]] = None):
    """
    Save image analysis results to DynamoDB.
    
    Args:
        analysis_id (str): Unique identifier for the analysis
        labels (list): List of detected image labels from Rekognition
        summary (str): Generated summary of the image content
        moderation (Optional[List[Dict[str, Any]]]): List of moderation labels if any inappropriate content detected
    """
    logger.info(f"Saving analysis {analysis_id} to DynamoDB")
    
    item = {
        "id": analysis_id,
        "labels": labels,
        "summary": summary,
    }
    
    # Only add moderation field if there are moderation labels
    if moderation:
        item["moderation"] = moderation
        
    table.put_item(Item=item)

@tracer.capture_method
def get_analysis(analysis_id: str):
    logger.info(f"Getting analysis {analysis_id} from DynamoDB")
    response = table.get_item(Key={"id": analysis_id})
    return response.get("Item")