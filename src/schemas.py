from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ImageAnalysisRequest(BaseModel):
    """
    Represents a request to analyze an image.
    
    Attributes:
        bucket (str): The S3 bucket where the image is stored.
        key (str): The S3 key of the image to be analyzed.
    """
    bucket: str = Field(..., description="The S3 bucket where the image is stored.")
    key: str = Field(..., description="The S3 key of the image to be analyzed.")

class ImageAnalysisResponse(BaseModel):
    analysis_id: str = Field(..., description="The unique ID for the analysis.")
    labels: List[Dict[str, Any]] = Field(..., description="A list of labels detected in the image.")
    summary: str = Field(..., description="A summary of the image analysis.")
    moderation_labels: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description="A list of moderation labels indicating potentially sensitive or inappropriate content. Empty or None if no issues detected."
    )