from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ImageAnalysisRequest(BaseModel):
    """
    Request model for image analysis API.
    
    Represents the input required to analyze an image stored in S3.
    """
    bucket: str = Field(..., description="The S3 bucket where the image is stored.")
    key: str = Field(..., description="The S3 key of the image to be analyzed.")

class ImageAnalysisResponse(BaseModel):
    """
    Response model for image analysis API.
    
    Contains the complete analysis results including labels, summary, and moderation findings.
    """
    analysis_id: str = Field(..., description="The unique ID for the analysis.")
    labels: List[Dict[str, Any]] = Field(..., description="A list of labels detected in the image.")
    summary: str = Field(..., description="A summary of the image analysis.")
    moderation: Optional[List[Dict[str, Any]]] = Field(default=None, description="Content moderation analysis results indicating potentially inappropriate content.")