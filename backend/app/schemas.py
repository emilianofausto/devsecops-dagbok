from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class DiaryEntryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Title cannot be empty")
    content: str = Field(..., min_length=1, description="Content cannot be empty")
    category: str = Field(..., min_length=1, max_length=50, description="Category cannot be empty")

class DiaryEntryCreate(DiaryEntryBase):
    pass

class DiaryEntryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, min_length=1, max_length=50)

class DiaryEntryResponse(DiaryEntryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True