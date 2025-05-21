from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging

from backend.api.arxiv_client import ArxivAPIClient, get_arxiv_client
from backend.schemas.arxiv_schema import ArxivPaper, ArxivSearchResponse, ArxivSearchRequest

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/search", response_model=ArxivSearchResponse, summary="Search arXiv papers by keyword")
async def search_arxiv_papers_post(
    request: ArxivSearchRequest,
    client: ArxivAPIClient = Depends(get_arxiv_client)
):
    """
    Search for papers on arXiv using a keyword provided in the request body.
    """
    try:
        papers = await client.search_papers(keyword=request.keyword, max_results=request.max_results)
        return ArxivSearchResponse(papers=papers, total_results=len(papers))
    except Exception as e:
        logger.error(f"Error searching arXiv with keyword '{request.keyword}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search arXiv: {str(e)}")

@router.get("/search", response_model=ArxivSearchResponse, summary="Search arXiv papers by keyword (GET)")
async def search_arxiv_papers_get(
    keyword: str = Query(..., description="Keyword to search for on arXiv"),
    max_results: Optional[int] = Query(10, description="Maximum number of results to return"),
    client: ArxivAPIClient = Depends(get_arxiv_client)
):
    """
    Search for papers on arXiv using a keyword provided as a query parameter.
    """
    try:
        papers = await client.search_papers(keyword=keyword, max_results=max_results)
        return ArxivSearchResponse(papers=papers, total_results=len(papers))
    except Exception as e:
        logger.error(f"Error searching arXiv with keyword '{keyword}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search arXiv: {str(e)}")
