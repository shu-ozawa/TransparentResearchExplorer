from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import logging

from backend.app.clients.gemini_client import GeminiClient
from typing import List
from backend.api.arxiv_client import ArxivClient

router = APIRouter()
logger = logging.getLogger(__name__)

class PaperInfo(BaseModel):
    title: str
    authors: List[str]
    abstract: str

class ScoreRequest(BaseModel):
    paper: PaperInfo
    query: str

class RelevanceScoreResponse(BaseModel):
    score: float
    explanation: str

# Pydantic model for search request
class SearchRequest(BaseModel):
    query: str

def get_gemini_client():
    return GeminiClient()

@router.post("/search", response_model=List[PaperInfo], summary="Search arXiv for papers matching the query")
async def search_papers(
    request: SearchRequest,
    arxiv_client: ArxivClient = Depends(ArxivClient)
):
    """
    Search arXiv for papers matching the query and return a list of paper metadata.
    """
    try:
        results = await arxiv_client.search(query=request.query, max_results=20)

        # Format the results as PaperInfo objects
        paper_list = []
        for result in results:
            paper = PaperInfo(
                title=result.title,
                authors=result.authors,
                abstract=result.summary or "",
            )
            paper_list.append(paper)

        return paper_list

    except Exception as e:
        logger.error(f"Error searching papers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search papers: {str(e)}")

@router.post("/score", response_model=RelevanceScoreResponse, summary="Generate relevance score and explanation for a paper-query pair")
async def generate_relevance_score(
    request: ScoreRequest,
    client: GeminiClient = Depends(get_gemini_client)
):
    """
    Generate a relevance score (0-1) and explanatory text for how relevant
    the given paper is to the query using the Gemini API.
    """

    # Create a prompt that combines the paper info with the query
    prompt = (
        f"Given the following research paper and query, rate its relevance on a scale of 0-1 (where 0 is not relevant and 1 is highly relevant). "
        f"Also provide a brief explanation for your rating.\n\n"
        f"Paper Title: {request.paper.title}\n"
        f"Authors: {', '.join(request.paper.authors)}\n"
        f"Abstract: {request.paper.abstract}\n\n"
        f"Query: {request.query}\n\n"
    )

    try:
        response_text = client.generate_text(prompt)

        # Extract score and explanation from the response
        score = None
        explanation = ""

        if "score:" in response_text.lower():
            # Try to extract a numeric score
            import re
            score_match = re.search(r"(\d+\.?\d*)", response_text)
            if score_match:
                try:
                    score = float(score_match.group(1))
                    if score < 0: score = 0
                    if score > 1: score = 1
                except ValueError:
                    score = None

        # If we couldn't extract a numeric score, default to trying to find a relevance level
        if not isinstance(score, float):
            relevance_levels = {
                "highly relevant": 0.9,
                "relevant": 0.7,
                "somewhat relevant": 0.5,
                "not very relevant": 0.3,
                "not relevant": 0
            }
            for level_text, value in relevance_levels.items():
                if level_text in response_text.lower():
                    score = value
                    break

        # Default to 0 if we couldn't determine a score
        if not isinstance(score, float):
            score = 0.0

        # Extract explanation (any text that isn't part of the score)
        explanation_parts = []
        lines = response_text.split("\n")
        in_explanation = False
        for line in lines:
            lower_line = line.lower()
            if "score:" in lower_line or any(level in lower_line for level in relevance_levels.keys()):
                continue  # Skip lines that contain the score

            # Skip numeric-only lines that might be standalone scores
            if re.match(r"^\d+\.?\d*$", line.strip()):
                continue

            explanation_parts.append(line)

        explanation = "\n".join(explanation_parts).strip()

        return RelevanceScoreResponse(score=score, explanation=explanation)
    except Exception as e:
        logger.error(f"Error generating relevance score: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate relevance score: {str(e)}")
