import os
import boto3
from typing import List, Dict, Any, Optional
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ.get("DDB_TABLE_NAME", ""))

@tracer.capture_method
def save_analysis(analysis_id: str, labels: List[Dict[str, Any]], summary: str, moderation_labels: Optional[List[Dict[str, Any]]] = None):
    """
    Save the analysis results to DynamoDB.
    
    Args:
        analysis_id (str): The unique ID for the analysis.
        labels (List[Dict[str, Any]]): A list of labels detected in the image.
        summary (str): A summary of the image analysis.
        moderation_labels (Optional[List[Dict[str, Any]]]): A list of moderation labels 
                         indicating potentially sensitive or inappropriate content. 
                         Empty or None if no issues detected.
    """
    logger.info(f"Saving analysis {analysis_id} to DynamoDB")
    item = {
        "id": analysis_id,
        "labels": labels,
        "summary": summary,
    }
    if moderation_labels is not None:
        item["moderation_labels"] = moderation_labels
    
    table.put_item(Item=item)
    logger.info(f"Successfully saved analysis {analysis_id} to DynamoDB")

@tracer.capture_method
def get_analysis(analysis_id: str):
    logger.info(f"Getting analysis {analysis_id} from DynamoDB")
    response = table.get_item(Key={"id": analysis_id})
    return response.get("Item")