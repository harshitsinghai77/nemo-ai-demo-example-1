from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ImageAnalysisRequest(BaseModel):
    bucket: str = Field(..., description="The S3 bucket where the image is stored.")
    key: str = Field(..., description="The S3 key of the image to be analyzed.")

class ImageAnalysisResponse(BaseModel):
    analysis_id: str = Field(..., description="The unique ID for the analysis.")
    labels: List[Dict[str, Any]] = Field(..., description="A list of labels detected in the image.")
    summary: str = Field(..., description="A summary of the image analysis.")
    moderation: List[Dict[str, Any]] = Field(default_factory=list, description="A list of content moderation findings. Empty if no issues detected.")