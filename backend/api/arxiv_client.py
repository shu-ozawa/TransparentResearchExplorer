import arxiv
import logging
from typing import List, Optional
from datetime import datetime
from arxiv import HTTPError as ArxivHTTPError, UnexpectedEmptyPageError as ArxivUnexpectedEmptyPageError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from backend.schemas.arxiv_schema import ArxivPaper, ArxivAuthor

logger = logging.getLogger(__name__)

class ArxivAPIClient:
    def __init__(self, default_max_results: int = 10):
        self.client = arxiv.Client()
        self.default_max_results = default_max_results

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=4, max=10),
           retry=retry_if_exception_type((ArxivHTTPError, ArxivUnexpectedEmptyPageError)))
    async def search_papers(self, keyword: str, max_results: Optional[int] = None) -> List[ArxivPaper]:
        """
        Search for papers on arXiv based on a keyword.

        Args:
            keyword: The keyword to search for.
            max_results: The maximum number of results to return. Defaults to self.default_max_results.

        Returns:
            A list of ArxivPaper objects.
        
        Raises:
            ArxivHTTPError: If there is an issue with the arXiv API request.
            ArxivUnexpectedEmptyPageError: If the arXiv API returns an empty page unexpectedly.
            Exception: For other unexpected errors.
        """
        if max_results is None:
            max_results = self.default_max_results

        search = arxiv.Search(
            query=keyword,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        try:
            results_generator = self.client.results(search)
            results = list(results_generator) # This is a blocking call

            papers = []
            for result in results:
                authors = [ArxivAuthor(name=author.name) for author in result.authors]
                paper = ArxivPaper(
                    entry_id=result.entry_id,
                    title=result.title,
                    authors=authors,
                    summary=result.summary,
                    published=result.published.replace(tzinfo=None), # Remove timezone for naive datetime
                    updated=result.updated.replace(tzinfo=None),   # Remove timezone for naive datetime
                    pdf_url=result.pdf_url,
                    categories=result.categories
                )
                papers.append(paper)
            return papers
        except ArxivHTTPError as e: # Use aliased exception
            logger.error(f"arXiv API HTTPError for keyword \'{keyword}\': {e}")
            raise
        except ArxivUnexpectedEmptyPageError as e: # Use aliased exception
            logger.error(f"arXiv API UnexpectedEmptyPageError for keyword \'{keyword}\': {e}")
            return [] 
        except Exception as e:
            logger.error(f"An unexpected error occurred during arXiv search for keyword \'{keyword}\': {e}")
            raise

async def get_arxiv_client() -> ArxivAPIClient:
    return ArxivAPIClient()
