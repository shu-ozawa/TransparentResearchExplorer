import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from backend.app.main import app # Assuming your FastAPI app instance is named 'app'
from backend.schemas.arxiv_schema import ArxivPaper, ArxivAuthor, ArxivSearchResponse
from backend.api.arxiv_client import ArxivAPIClient # To mock its methods
from datetime import datetime

# This fixture will be used by tests that need a TestClient instance
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_arxiv_paper_data():
    return ArxivPaper(
        entry_id="2301.00001v1",
        title="Mock Paper 1",
        authors=[ArxivAuthor(name="Dr. Mock A.")],
        summary="This is a mock paper summary.",
        published=datetime(2023, 1, 1, 10, 0, 0),
        updated=datetime(2023, 1, 2, 10, 0, 0),
        pdf_url="http://arxiv.org/pdf/2301.00001v1",
        categories=["cs.AI"]
    )

@pytest.mark.asyncio
async def test_search_arxiv_papers_post_success(client: TestClient, mock_arxiv_paper_data: ArxivPaper, mocker):
    # Mock the ArxivAPIClient.search_papers method
    mock_search_papers = AsyncMock(return_value=[mock_arxiv_paper_data])
    mocker.patch('backend.api.arxiv_client.ArxivAPIClient.search_papers', new=mock_search_papers)

    request_data = {"keyword": "test query", "max_results": 1}
    response = client.post("/api/arxiv/search", json=request_data)

    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["papers"]) == 1
    assert response_data["papers"][0]["title"] == "Mock Paper 1"
    assert response_data["total_results"] == 1
    mock_search_papers.assert_called_once_with(keyword="test query", max_results=1)

@pytest.mark.asyncio
async def test_search_arxiv_papers_get_success(client: TestClient, mock_arxiv_paper_data: ArxivPaper, mocker):
    mock_search_papers = AsyncMock(return_value=[mock_arxiv_paper_data])
    mocker.patch('backend.api.arxiv_client.ArxivAPIClient.search_papers', new=mock_search_papers)

    response = client.get("/api/arxiv/search?keyword=test%20query&max_results=1")

    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["papers"]) == 1
    assert response_data["papers"][0]["title"] == "Mock Paper 1"
    assert response_data["total_results"] == 1
    mock_search_papers.assert_called_once_with(keyword="test query", max_results=1)

@pytest.mark.asyncio
async def test_search_arxiv_papers_post_client_error(client: TestClient, mocker):
    mock_search_papers = AsyncMock(side_effect=Exception("Arxiv Client Failed"))
    mocker.patch('backend.api.arxiv_client.ArxivAPIClient.search_papers', new=mock_search_papers)

    request_data = {"keyword": "error query", "max_results": 5}
    response = client.post("/api/arxiv/search", json=request_data)

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to search arXiv: Arxiv Client Failed"}
    mock_search_papers.assert_called_once_with(keyword="error query", max_results=5)

@pytest.mark.asyncio
async def test_search_arxiv_papers_get_client_error(client: TestClient, mocker):
    mock_search_papers = AsyncMock(side_effect=Exception("Arxiv Client Failed GET"))
    mocker.patch('backend.api.arxiv_client.ArxivAPIClient.search_papers', new=mock_search_papers)

    response = client.get("/api/arxiv/search?keyword=error%20query&max_results=2")

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to search arXiv: Arxiv Client Failed GET"}
    mock_search_papers.assert_called_once_with(keyword="error query", max_results=2)

@pytest.mark.asyncio
async def test_search_arxiv_papers_post_validation_error(client: TestClient):
    # Missing keyword
    request_data = {"max_results": 1}
    response = client.post("/api/arxiv/search", json=request_data)
    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation errors

    # Invalid max_results type
    request_data = {"keyword": "test", "max_results": "not-an-int"}
    response = client.post("/api/arxiv/search", json=request_data)
    assert response.status_code == 422
