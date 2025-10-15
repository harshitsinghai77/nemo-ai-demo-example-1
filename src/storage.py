import os
import boto3
from typing import List, Dict, Any, Optional
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ.get("DDB_TABLE_NAME", ""))

@tracer.capture_method
def save_analysis(analysis_id: str, labels: List[Dict[str, Any]], summary: str, moderation_labels: Optional[List[Dict[str, Any]]] = None) -> None:
    logger.info(f"Saving analysis {analysis_id} to DynamoDB")
    item = {
        "id": analysis_id,
        "labels": labels,
        "summary": summary,
    }
    
    # Only add moderation_labels if it has content
    if moderation_labels:
        item["moderation_labels"] = moderation_labels
    
    table.put_item(Item=item)

@tracer.capture_method
def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    logger.info(f"Getting analysis {analysis_id} from DynamoDB")
    response = table.get_item(Key={"id": analysis_id})
    item = response.get("Item")
    
    if item:
        # Ensure moderation_labels field exists for backward compatibility
        if "moderation_labels" not in item:
            item["moderation_labels"] = []
    
    return item