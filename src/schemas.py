from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ImageAnalysisRequest(BaseModel):
    bucket: str = Field(..., description="The S3 bucket where the image is stored.")
    key: str = Field(..., description="The S3 key of the image to be analyzed.")

class ImageAnalysisResponse(BaseModel):
    analysis_id: str = Field(..., description="The unique ID for the analysis.")
    labels: List[Dict[str, Any]] = Field(..., description="A list of labels detected in the image.")
    summary: str = Field(..., description="A summary of the image analysis.")
    moderation_labels: Optional[List[Dict[str, Any]]] = Field(default=None, description="Content moderation findings. Empty or None if no inappropriate content is detected.")