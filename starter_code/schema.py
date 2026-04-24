from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, Optional
from datetime import datetime

# ==========================================
# ROLE 1: LEAD DATA ARCHITECT
# ==========================================
# Your task is to define the Unified Schema for all sources.
# This is v1. Note: A breaking change is coming at 11:00 AM!

class UnifiedDocument(BaseModel):
    # v1 schema
    document_id: str = Field(..., min_length=1, description="Unique identifier for the document")
    content: str = Field(..., min_length=1, description="The main text or extracted data")
    source_type: Literal["PDF", "CSV", "HTML", "Video", "Code", "Legacy"] = Field(
        ..., description="Source of the data"
    )
    author: str = Field("Unknown", description="Author of the document")
    timestamp: Optional[datetime] = Field(None, description="When the document was created or processed")
    source_metadata: Dict[str, Any] = Field(default_factory=dict, description="Source-specific metadata")
    
    # Optional: status for quality gate tracking
    quality_score: float = Field(1.0, ge=0.0, le=1.0, description="Score from quality gate (0.0 to 1.0)")
    is_valid: bool = Field(True, description="Flag for validity after quality check")
