from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import logging
import re

from backend.app.clients.gemini_client import GeminiClient
from typing import List, Optional
from backend.api.arxiv_client import ArxivAPIClient

router = APIRouter()
logger = logging.getLogger(__name__)

class PaperInfo(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    relevance_score: Optional[float] = None
    published: str
    categories: List[str]

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

async def _calculate_relevance_score(title: str, authors: List[str], abstract: str, query: str, client: GeminiClient) -> Optional[float]:
    """
    Helper function to calculate relevance score for a paper and query.
    Returns a float score (0-1) or None if scoring fails.
    """
    prompt = (
        f"Given the following research paper and query, rate its relevance on a scale of 0-1 (where 0 is not relevant and 1 is highly relevant).\n\n"
        f"Paper Title: {title}\n"
        f"Authors: {', '.join(authors)}\n"
        f"Abstract: {abstract}\n\n"
        f"Query: {query}\n\n"
        f"Score:"
    )
    try:
        response_text = client.generate_text(prompt)
        # Extract score from the response
        score = None

        # Define relevance levels
        relevance_levels = {
            "highly relevant": 0.9,
            "relevant": 0.7,
            "somewhat relevant": 0.5,
            "not very relevant": 0.3,
            "not relevant": 0
        }

        # Try to extract score from "Rating: X.X" or "Score: X.X" format
        rating_match = re.search(r"(?:Rating|Score):\s*(\d+\.?\d*)", response_text, re.IGNORECASE)
        if rating_match:
            try:
                score_val = float(rating_match.group(1))
                score = max(0.0, min(1.0, score_val)) # Clamp between 0 and 1
            except ValueError:
                score = None
        
        # If no rating found, try to find a number, potentially a raw score
        if not isinstance(score, float):
            # Search for a floating point number or an integer that could be a score
            score_match = re.search(r"(\d+\.?\d*)", response_text)
            if score_match:
                try:
                    score_val = float(score_match.group(1))
                    # If the number is like 8 or 9, and context suggests 0-10 scale, normalize it
                    if score_val > 1 and score_val <=10:
                         score_val = score_val / 10.0
                    score = max(0.0, min(1.0, score_val)) # Clamp between 0 and 1
                except ValueError:
                    score = None

        # If still no score, try relevance levels from text
        if not isinstance(score, float):
            for level_text, value in relevance_levels.items():
                if level_text in response_text.lower():
                    score = value
                    break
        
        # If score is found, ensure it's within 0-1 range
        if isinstance(score, float):
            score = max(0.0, min(1.0, score))
            return score
        
        # Try to find a score without "Score:" or "Rating:" prefix
        # This regex looks for a floating point number (e.g., 0.8, .7) or an integer.
        direct_score_match = re.search(r"^\s*(\d(\.\d+)?)\s*$", response_text, re.MULTILINE)
        if direct_score_match:
            try:
                score_val = float(direct_score_match.group(1))
                score = max(0.0, min(1.0, score_val)) # Clamp between 0 and 1
                return score
            except ValueError:
                pass # score remains None

        logger.debug(f"Could not parse score from response: '{response_text}' for query '{query}' and title '{title}'")
        return None
    except Exception as e:
        logger.error(f"Error generating relevance score for '{title}': {e}")
        return None

@router.post("/search", response_model=List[PaperInfo], summary="Search arXiv for papers matching the query")
async def search_papers(
    request: SearchRequest,
    arxiv_client: ArxivAPIClient = Depends(ArxivAPIClient),
    client: GeminiClient = Depends(get_gemini_client) # Added GeminiClient
):
    """
    Search arXiv for papers matching the query and return a list of paper metadata.
    """
    try:
        results = await arxiv_client.search_papers(keyword=request.query, max_results=20) # Kept max_results as is

        # Format the results as PaperInfo objects
        paper_list = []
        for result in results:
            authors = [author.name for author in result.authors]
            abstract = result.summary or ""
            title = result.title

            # Calculate relevance score
            relevance_score = await _calculate_relevance_score(
                title=title,
                authors=authors,
                abstract=abstract,
                query=request.query,
                client=client
            )

            published_date = result.published.isoformat()
            paper_categories = result.categories

            paper = PaperInfo(
                title=title,
                authors=authors,
                abstract=abstract,
                relevance_score=relevance_score, # Included relevance_score
                published=published_date,
                categories=paper_categories
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

        # Define relevance levels
        relevance_levels = {
            "highly relevant": 0.9,
            "relevant": 0.7,
            "somewhat relevant": 0.5,
            "not very relevant": 0.3,
            "not relevant": 0
        }

        # Try to extract score from "Rating: X.X" format
        rating_match = re.search(r"Rating:\s*(\d+\.?\d*)", response_text)
        if rating_match:
            try:
                score = float(rating_match.group(1))
                if score < 0: score = 0
                if score > 1: score = 1
            except ValueError:
                score = None

        # If no rating found, try other formats
        if not isinstance(score, float):
            if "score:" in response_text.lower():
                score_match = re.search(r"(\d+\.?\d*)", response_text)
                if score_match:
                    try:
                        score = float(score_match.group(1))
                        if score < 0: score = 0
                        if score > 1: score = 1
                    except ValueError:
                        score = None

        # If still no score, try relevance levels
        if not isinstance(score, float):
            for level_text, value in relevance_levels.items():
                if level_text in response_text.lower():
                    score = value
                    break

        # Default to 0 if we couldn't determine a score
        if not isinstance(score, float):
            score = 0.0

        # Extract explanation (any text that isn't part of the score/rating)
        explanation_parts = []
        lines = response_text.split("\n")
        for line in lines:
            lower_line = line.lower()
            if "rating:" in lower_line or "score:" in lower_line or any(level in lower_line for level in relevance_levels.keys()):
                continue  # Skip lines that contain the score/rating

            # Skip numeric-only lines that might be standalone scores
            if re.match(r"^\d+\.?\d*$", line.strip()):
                continue

            explanation_parts.append(line)

        explanation = "\n".join(explanation_parts).strip()

        return RelevanceScoreResponse(score=score, explanation=explanation)
    except Exception as e:
        logger.error(f"Error generating relevance score: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate relevance score: {str(e)}")
