"""Data models for Cloud Assessment Microservice."""
from typing import Optional
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Payload to create a new task/item."""
    title: str = Field(..., min_length=1, max_length=100, description="Title of the item")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description")
    status: str = Field("pending", description="Status of the item (pending, in_progress, completed)")
    priority: str = Field("normal", description="Priority level (low, normal, high)")


class ItemResponse(BaseModel):
    """Item representation returned by the API."""
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    created_at: str


class HealthResponse(BaseModel):
    """Health check response format."""
    status: str
    service: str
    version: str
    uptime_seconds: float


class SystemInfoResponse(BaseModel):
    """System information returned for cloud deployment verification."""
    service: str
    version: str
    hostname: str
    platform: str
    python_version: str
    environment: str
