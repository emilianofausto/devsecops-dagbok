from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class DiaryEntryBase(BaseModel):
    """Base schema containing common attributes for a diary entry."""
    title: str = Field(..., min_length=1, max_length=100, description="Title cannot be empty")
    content: str = Field(..., min_length=1, description="Content cannot be empty")
    category: str = Field(..., min_length=1, max_length=50, description="Category cannot be empty")

class DiaryEntryCreate(DiaryEntryBase):
    """Schema for creating a new diary entry."""

class DiaryEntryUpdate(BaseModel):
    """Schema for updating an existing diary entry. All fields are optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, min_length=1, max_length=50)

class DiaryEntryResponse(DiaryEntryBase):
    """Schema for the API response representing a diary entry."""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
