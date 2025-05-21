from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ArxivAuthor(BaseModel):
    name: str

class ArxivPaper(BaseModel):
    entry_id: str = Field(..., description="arXiv ID of the paper")
    title: str = Field(..., description="Title of the paper")
    authors: List[ArxivAuthor] = Field(..., description="Authors of the paper")
    summary: str = Field(..., description="Abstract of the paper")
    published: datetime = Field(..., description="Date the paper was published")
    updated: datetime = Field(..., description="Date the paper was last updated")
    pdf_url: Optional[str] = Field(None, description="URL to the PDF of the paper")
    categories: List[str] = Field(..., description="Categories of the paper")

class ArxivSearchRequest(BaseModel):
    keyword: str = Field(..., description="Keyword to search for on arXiv")
    max_results: int = Field(10, description="Maximum number of results to return")

class ArxivSearchResponse(BaseModel):
    papers: List[ArxivPaper]
    total_results: int
