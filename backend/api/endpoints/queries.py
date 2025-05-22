from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import logging

from backend.app.clients.gemini_client import GeminiClient
from backend.api.arxiv_client import ArxivAPIClient, get_arxiv_client
from backend.models.paper import Paper
from backend.core.database import get_db
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

class QueryGenerationRequest(BaseModel):
    initial_keywords: str

class RelatedQuery(BaseModel):
    query: str
    description: str

class QueryGenerationResponse(BaseModel):
    original_query: str
    related_queries: list[RelatedQuery]

def get_gemini_client():
    return GeminiClient()

@router.post("/generate", response_model=QueryGenerationResponse, summary="Generate related queries from initial keywords")
async def generate_related_queries(
    request: QueryGenerationRequest,
    client: GeminiClient = Depends(get_gemini_client)
):
    """
    Generate a list of related queries from the given initial keywords using the Gemini API.
    """
    prompt = f"Given the following research topic: '{request.initial_keywords}', generate 5-7 related search queries. For each query, also provide a brief description of what it focuses on."

    try:
        response_text = client.generate_text(prompt)

        # Parse the response to extract related queries
        related_queries = []
        if "1." in response_text or "\n" in response_text:
            # Handle numbered list format (if Gemini returns it that way)
            sections = response_text.split("\n\n")
            for section in sections:
                if "1." in section or "2." in section:  # Check for numbered items
                    lines = section.strip().split("\n")
                    query_line = lines[0]
                    description_lines = lines[1:]
                    description = " ".join(description_lines)

                    # Extract the actual query text (remove numbering)
                    if ". " in query_line:
                        query_text = query_line.split(". ", 1)[1]
                    else:
                        query_text = query_line

                    related_queries.append(RelatedQuery(query=query_text, description=description))
                elif ":" in section:  # Handle query: description format
                    parts = section.split(":", 1)
                    query_text = parts[0].strip()
                    description = parts[1].strip()
                    related_queries.append(RelatedQuery(query=query_text, description=description))

        return QueryGenerationResponse(
            original_query=request.initial_keywords,
            related_queries=related_queries or [
                RelatedQuery(query="No related queries found", description="")
            ]
        )
    except Exception as e:
        logger.error(f"Error generating related queries for '{request.initial_keywords}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate related queries: {str(e)}")

class SearchQuery(BaseModel):
    query: str
    max_results: int = 10

class PaperSearchResponse(BaseModel):
    title: str
    authors: List[str]
    summary: str
    published_date: datetime
    url: str

@router.post("/search", response_model=List[PaperSearchResponse], summary="Search arXiv papers by query list and cache results")
async def search_papers(
    queries: List[SearchQuery],
    db: Session = Depends(get_db),
    client: ArxivAPIClient = Depends(get_arxiv_client)
):
    """
    Search for papers on arXiv using a list of queries, integrate the results,
    cache the results in the database, and return basic information.
    """
    all_papers = []

    for search_query in queries:
        # Get cached papers
        result_ids = []
        results = await client.search_papers(keyword=search_query.query, max_results=search_query.max_results)
        for result in results:
            result_ids.append(result.entry_id)

        cached_papers = db.query(Paper).filter(Paper.arxiv_id.in_(result_ids)).all()

        if not cached_papers:
            try:
                # If no cache, save the new results
                for result in results:
                    authors = [author.name for author in result.authors]
                    paper = Paper(
                        arxiv_id=result.entry_id,
                        title=result.title,
                        authors=authors,
                        abstract=result.summary,
                        published_date=result.published,
                        url=result.pdf_url
                    )
                    db.add(paper)
                    all_papers.append(PaperSearchResponse(
                        title=paper.title,
                        authors=authors,
                        summary=paper.abstract,
                        published_date=paper.published_date,
                        url=paper.url
                    ))

                db.commit()
            except Exception as e:
                logger.error(f"Error searching arXiv with query '{search_query.query}': {e}")
                raise HTTPException(status_code=500, detail=f"Failed to search arXiv: {str(e)}")
        else:
            # If cache exists, use the cached papers
            for paper in cached_papers:
                all_papers.append(PaperSearchResponse(
                    title=paper.title,
                    authors=paper.authors,
                    summary=paper.abstract,
                    published_date=paper.published_date,
                    url=paper.url
                ))

    return all_papers
