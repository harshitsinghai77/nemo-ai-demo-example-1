import os
import boto3
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ.get("DDB_TABLE_NAME", ""))

@tracer.capture_method
def save_analysis(analysis_id: str, labels: list, summary: str):
    logger.info(f"Saving analysis {analysis_id} to DynamoDB")
    table.put_item(
        Item={
            "id": analysis_id,
            "labels": labels,
            "summary": summary,
        }
    )

@tracer.capture_method
def get_analysis(analysis_id: str):
    logger.info(f"Getting analysis {analysis_id} from DynamoDB")
    response = table.get_item(Key={"id": analysis_id})
    return response.get("Item")