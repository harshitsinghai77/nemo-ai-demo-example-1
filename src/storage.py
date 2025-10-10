import os
import boto3
from typing import Optional, List, Dict, Any
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ.get("DDB_TABLE_NAME", ""))

@tracer.capture_method
def save_analysis(analysis_id: str, labels: list, summary: str, moderation_labels: Optional[List[Dict[str, Any]]] = None):
    logger.info(f"Saving analysis {analysis_id} to DynamoDB")
    analysis_item = {
        "id": analysis_id,
        "labels": labels,
        "summary": summary,
    }
    
    if moderation_labels is not None:
        analysis_item["moderation_labels"] = moderation_labels
        logger.info(f"Added {len(moderation_labels)} moderation labels to analysis {analysis_id}")
    
    table.put_item(Item=analysis_item)

@tracer.capture_method
def get_analysis(analysis_id: str):
    logger.info(f"Getting analysis {analysis_id} from DynamoDB")
    response = table.get_item(Key={"id": analysis_id})
    stored_analysis = response.get("Item")
    
    # Ensure backwards compatibility for existing records without moderation_labels
    # This handles cases where analyses were stored before the moderation feature was added
    if stored_analysis and "moderation_labels" not in stored_analysis:
        stored_analysis["moderation_labels"] = []
        logger.info(f"Added empty moderation_labels for backwards compatibility in analysis {analysis_id}")
    elif stored_analysis and stored_analysis.get("moderation_labels") is None:
        # Explicitly handle None values
        stored_analysis["moderation_labels"] = []
    
    return stored_analysis