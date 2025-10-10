import os
import boto3
from aws_lambda_powertools import Logger, Tracer
from typing import Optional, List, Dict, Any

logger = Logger()
tracer = Tracer()

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ.get("DDB_TABLE_NAME", ""))

@tracer.capture_method
def save_analysis(analysis_id: str, labels: List[Dict[str, Any]], summary: str, moderation: Optional[List[Dict[str, Any]]] = None) -> None:
    logger.info(f"Saving analysis {analysis_id} to DynamoDB")
    item = {
        "id": analysis_id,
        "labels": labels,
        "summary": summary,
    }
    
    # Only add moderation field if it has content (not empty list)
    if moderation:
        item["moderation"] = moderation
    
    table.put_item(Item=item)

@tracer.capture_method
def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    logger.info(f"Getting analysis {analysis_id} from DynamoDB")
    response = table.get_item(Key={"id": analysis_id})
    return response.get("Item")