from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    CfnOutput,
    Duration,
)
from constructs import Construct

class AiImageAnalyzerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        uploads_bucket = s3.Bucket(self, "UploadsBucket",
            bucket_name=f"{self.stack_name.lower()}-uploads"
        )

        analysis_table = dynamodb.Table(self, "ImageAnalysisTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            read_capacity=1,
            write_capacity=1
        )

        rekognition_policy = iam.PolicyStatement(
            actions=["rekognition:DetectLabels", "rekognition:DetectModerationLabels"],
            resources=["*"]
        )

        bedrock_policy = iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=["*"]
        )

        analysis_function = _lambda.Function(self, "ImageAnalysisFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.handler",
            code=_lambda.Code.from_asset("."),
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "POWERTOOLS_SERVICE_NAME": "ai-image-analyzer",
                "POWERTOOLS_METRICS_NAMESPACE": "MyCoolApp",
                "LOG_LEVEL": "INFO",
                "DDB_TABLE_NAME": analysis_table.table_name,
            },
            architecture=_lambda.Architecture.X86_64,
            layers=[
                _lambda.LayerVersion.from_layer_version_arn(
                    self, "PowertoolsLayer",
                    layer_version_arn=f"arn:aws:lambda:{self.region}:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64:18"
                )
            ]
        )

        uploads_bucket.grant_read(analysis_function)
        analysis_table.grant_read_write_data(analysis_function)
        analysis_function.add_to_role_policy(rekognition_policy)
        analysis_function.add_to_role_policy(bedrock_policy)

        fn_url = analysis_function.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE
        )

        CfnOutput(self, "ImageAnalysisApi",
            description="API Gateway endpoint URL for Image Analysis function",
            value=fn_url.url
        )
