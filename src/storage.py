import os
import boto3
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ.get("DDB_TABLE_NAME", ""))

@tracer.capture_method
def save_analysis(analysis_id: str, labels: list, summary: str, moderation: list = None):
    """
    Save analysis results including moderation data to DynamoDB.
    Moderation defaults to empty list if not provided.
    """
    logger.info(f"Saving analysis {analysis_id} to DynamoDB")
    
    # Ensure moderation is always a list
    if moderation is None:
        moderation = []
    
    table.put_item(
        Item={
            "id": analysis_id,
            "labels": labels,
            "summary": summary,
            "moderation": moderation,
        }
    )

@tracer.capture_method
def get_analysis(analysis_id: str):
    logger.info(f"Getting analysis {analysis_id} from DynamoDB")
    response = table.get_item(Key={"id": analysis_id})
    item = response.get("Item")
    
    # Ensure backward compatibility: add empty moderation field if missing
    if item and "moderation" not in item:
        item["moderation"] = []
    
    return item