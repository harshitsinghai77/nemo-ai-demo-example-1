# AI Image Analyzer

This project is a serverless application that analyzes images using AWS Rekognition and generates descriptive summaries with Amazon Bedrock. The application is built with the AWS Serverless Application Model (SAM) and uses AWS Lambda, Amazon S3, Amazon DynamoDB, and Amazon API Gateway.

## Architecture

The application consists of the following components:

- **Amazon S3 Bucket**: Stores the images to be analyzed.
- **AWS Lambda Function**: Contains the core application logic, triggered by an API Gateway endpoint.
- **Amazon DynamoDB Table**: Stores the results of the image analysis.
- **Amazon Rekognition**: Detects labels in the images and performs content moderation.
- **Amazon Bedrock**: Generates descriptive summaries of the images based on the detected labels.
- **Amazon API Gateway**: Provides a RESTful API to trigger the image analysis and retrieve the results.

## Features

- **Image Analysis**: Upload an image to the S3 bucket and trigger the analysis via an API endpoint.
- **Label Detection**: Uses Amazon Rekognition to identify objects, scenes, and concepts in the images.
- **Content Moderation**: Uses Amazon Rekognition to detect inappropriate, sensitive, or offensive content in images.
- **Descriptive Summaries**: Uses Amazon Bedrock to generate human-readable summaries of the image content.
- **Result Storage**: Stores the analysis results in a DynamoDB table for later retrieval.
- **RESTful API**: Provides endpoints to initiate the analysis and fetch the results.

## Content Moderation

The system now includes content moderation capabilities that assess whether images contain potentially inappropriate or sensitive material. This includes detection of:

- Explicit nudity and suggestive content
- Violence and disturbing imagery  
- Drug and tobacco-related content
- Rude gestures and offensive symbols

Moderation results are included in the API response with confidence scores and category labels. If no moderation issues are detected, the field will be empty or contain an empty list.

## Deployment

To deploy the application, you need to have the AWS CDK CLI installed. You can then build and deploy the application using the following commands:

```bash
cdk deploy
```

## Usage

Once the application is deployed, you can use the API Gateway endpoint to interact with it.

### Trigger Image Analysis

To trigger the image analysis, send a POST request to the `/images` endpoint with the following JSON body:

```json
{
  "bucket": "<your-s3-bucket-name>",
  "key": "<your-image-key>"
}
```

### Get Analysis Results

To get the analysis results, send a GET request to the `/images/{analysis_id}` endpoint, where `{analysis_id}` is the ID returned by the initial analysis request.

The response will include:
- `labels`: Detected objects and concepts in the image
- `summary`: AI-generated description of the image
- `moderation_labels`: Content moderation findings (if any inappropriate content is detected)