import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import arxiv # Keep this for spec
from datetime import datetime
from tenacity import RetryError # Import RetryError

# Import the aliased exceptions, same as in arxiv_client.py
from arxiv import HTTPError as ArxivHTTPError, UnexpectedEmptyPageError as ArxivUnexpectedEmptyPageError

from backend.api.arxiv_client import ArxivAPIClient
from backend.schemas.arxiv_schema import ArxivPaper, ArxivAuthor

@pytest.fixture
def arxiv_client_fixture(): # Renamed to avoid conflict if a test function is named arxiv_client
    return ArxivAPIClient(default_max_results=5)

@pytest.mark.asyncio
async def test_search_papers_success(arxiv_client_fixture: ArxivAPIClient, mocker):
    mock_author1 = MagicMock()
    mock_author1.name = "Author One"
    mock_author2 = MagicMock()
    mock_author2.name = "Author Two"

    mock_arxiv_result = MagicMock(spec=arxiv.Result)
    mock_arxiv_result.entry_id = "1234.5678v1"
    mock_arxiv_result.title = "Test Paper Title"
    mock_arxiv_result.authors = [mock_author1, mock_author2]
    mock_arxiv_result.summary = "This is a test summary."
    mock_arxiv_result.published = datetime(2023, 1, 1, 12, 0, 0)
    mock_arxiv_result.updated = datetime(2023, 1, 2, 12, 0, 0)
    mock_arxiv_result.pdf_url = "http://arxiv.org/pdf/1234.5678v1"
    mock_arxiv_result.categories = ["cs.AI", "cs.LG"]

    mocker.patch.object(arxiv_client_fixture.client, 'results', return_value=[mock_arxiv_result])
    
    keyword = "test keyword"
    max_results = 1
    papers = await arxiv_client_fixture.search_papers(keyword, max_results=max_results)

    assert len(papers) == 1
    paper = papers[0]
    assert isinstance(paper, ArxivPaper)
    assert paper.entry_id == "1234.5678v1"
    assert paper.title == "Test Paper Title"
    assert len(paper.authors) == 2
    assert paper.authors[0].name == "Author One"
    assert paper.summary == "This is a test summary."
    assert paper.published == datetime(2023, 1, 1, 12, 0, 0)
    assert paper.pdf_url == "http://arxiv.org/pdf/1234.5678v1"
    assert paper.categories == ["cs.AI", "cs.LG"]

@pytest.mark.asyncio
async def test_search_papers_empty_results(arxiv_client_fixture: ArxivAPIClient, mocker):
    mocker.patch.object(arxiv_client_fixture.client, 'results', return_value=[])
    
    keyword = "empty keyword"
    papers = await arxiv_client_fixture.search_papers(keyword)

    assert len(papers) == 0

@pytest.mark.asyncio
async def test_search_papers_http_error(arxiv_client_fixture: ArxivAPIClient, mocker):
    mock_exception = ArxivHTTPError(
        "http://test.com",  # url
        500,                # status
        "Test HTTP Error"   # message
    )
    # Patch the 'results' method on the *instance* of the client used in the test
    mocked_results_method = mocker.patch.object(arxiv_client_fixture.client, 'results', side_effect=mock_exception)
    
    keyword = "error keyword"
    with pytest.raises(RetryError) as excinfo:
        await arxiv_client_fixture.search_papers(keyword)
    
    assert isinstance(excinfo.value.__cause__, ArxivHTTPError)
    # Verify that the mocked method was called, e.g., 3 times due to retry
    assert mocked_results_method.call_count == 3 # Assuming 3 attempts from @retry

@pytest.mark.asyncio
async def test_search_papers_unexpected_empty_page_error(arxiv_client_fixture: ArxivAPIClient, mocker):
    mock_exception = ArxivUnexpectedEmptyPageError(
        "http://test.com",  # url
        b"",                # raw_feed
        0                   # retry
    )
    # Patch the 'results' method on the *instance* of the client used in the test
    mocked_results_method = mocker.patch.object(arxiv_client_fixture.client, 'results', side_effect=mock_exception)
    
    keyword = "empty page keyword"
    papers = await arxiv_client_fixture.search_papers(keyword)
    
    assert papers == []
    # Verify that the mocked method was called once, as ArxivUnexpectedEmptyPageError is handled directly
    assert mocked_results_method.call_count == 1


@pytest.mark.asyncio
async def test_search_papers_uses_default_max_results(arxiv_client_fixture: ArxivAPIClient, mocker):
    mock_author1 = MagicMock()
    mock_author1.name = "Default Author"

    mock_arxiv_result = MagicMock(spec=arxiv.Result)
    mock_arxiv_result.entry_id = "default.id"
    mock_arxiv_result.title = "Default Title"
    mock_arxiv_result.authors = [mock_author1]
    mock_arxiv_result.summary = "Default summary."
    mock_arxiv_result.published = datetime(2023, 1, 1)
    mock_arxiv_result.updated = datetime(2023, 1, 1)
    mock_arxiv_result.pdf_url = "http://default.pdf"
    mock_arxiv_result.categories = ["cs.XX"]

    mock_client_results = mocker.patch.object(arxiv_client_fixture.client, 'results', return_value=[mock_arxiv_result] * 5)
    mocker.patch('arxiv.Search', return_value=MagicMock())

    keyword = "default results"
    await arxiv_client_fixture.search_papers(keyword) 

    arxiv.Search.assert_called_once_with(
        query=keyword,
        max_results=arxiv_client_fixture.default_max_results, 
        sort_by=arxiv.SortCriterion.Relevance
    )
    assert mock_client_results.call_count == 1
