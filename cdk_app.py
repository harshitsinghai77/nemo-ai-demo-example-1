import aws_cdk as cdk
from infrastructure.ai_image_analyzer_stack import AiImageAnalyzerStack

app = cdk.App()
AiImageAnalyzerStack(app, "AiImageAnalyzerStack")
app.synth()
