import os
import boto3
from typing import Optional, List, Dict, Any
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ.get("DDB_TABLE_NAME", ""))

@tracer.capture_method
def save_analysis(analysis_id: str, labels: List[Dict[str, Any]], summary: str, moderation_labels: Optional[List[Dict[str, Any]]] = None):
    logger.info(f"Saving analysis {analysis_id} to DynamoDB")
    item = {
        "id": analysis_id,
        "labels": labels,
        "summary": summary,
    }
    
    # Only add moderation_labels if they exist to maintain backward compatibility
    if moderation_labels is not None:
        item["moderation_labels"] = moderation_labels
        
    table.put_item(Item=item)

@tracer.capture_method
def get_analysis(analysis_id: str):
    logger.info(f"Getting analysis {analysis_id} from DynamoDB")
    response = table.get_item(Key={"id": analysis_id})
    return response.get("Item")