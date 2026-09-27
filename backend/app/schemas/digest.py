from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DigestRequest(BaseModel):
    topic: str = Field(..., description="Topic of the digest, e.g., 'Technology', 'Healthcare', 'Viral News'")
    date_str: Optional[str] = Field(default=None, description="Date in YYYY-MM-DD format. Defaults to today.")
    claim_ids: Optional[List[str]] = Field(default=None, description="Specific claim IDs to include, or None to auto-compile")
    query_news: Optional[str] = Field(default=None, description="Optional search term to discover latest verified news for digest")

class DigestResponse(BaseModel):
    id: str
    title: str
    topic: str
    date_str: str
    claim_count: int
    claim_ids: List[str]
    markdown_content: str
    created_at: str

class ExportMarkdownRequest(BaseModel):
    target_type: str = Field(..., description="'digest' or 'claim'")
    id: str = Field(..., description="The ID of the digest or claim to export")
