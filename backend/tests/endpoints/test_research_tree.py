import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from datetime import datetime
from typing import List

# Modules to test
from backend.api.endpoints.research_tree import (
    ResearchTreeRequest,
    ScoredPaper,
    QueryNode,
    SearchTreeResponse,
    _generate_research_plan,
    _calculate_relevance_score,
    _deduplicate_papers,
    research_tree_search
)

# Clients to mock
# GeminiClient and OllamaClient might be used for spec if specific client behavior is tested,
# but for generic LLM client mocking, a simple MagicMock is often sufficient.
# from backend.app.clients.gemini_client import GeminiClient 
# from backend.app.clients.ollama_client import OllamaClient
from backend.api.arxiv_client import ArxivAPIClient

# For creating mock Arxiv paper objects
from backend.schemas.arxiv_schema import ArxivPaper as MockArxivPaperSchema, ArxivAuthor


class TestGenerateResearchPlan(unittest.IsolatedAsyncioTestCase):
    async def test_successful_plan_generation(self):
        mock_llm_client = MagicMock() # Changed from mock_gemini_client
        mock_llm_client.generate_text = MagicMock(return_value=(
            "Research Goal: Understand the applications of AI in healthcare.\n\n" # Assuming this is the direct output from generate_text now
            "Search Queries:\n"
            "1. Query: AI diagnostics healthcare | Description: AI techniques for medical diagnosis.\n"
            "2. Query: machine learning drug discovery | Description: ML in pharmaceutical research."
        ))
        
        natural_query = "AI in healthcare"
        max_queries = 2
        
        # The _generate_research_plan function was updated to parse the goal from the response.
        # Let's assume the parsing logic within _generate_research_plan handles goal extraction correctly.
        # The test here should focus on the interaction with the client.
        # For the purpose of this test, we'll assume the client output format is what _generate_research_plan expects.
        # The internal logic of _generate_research_plan (goal parsing) is tested by its own unit tests.
        
        # If _generate_research_plan's first return value (goal) is directly from the response,
        # we need to adjust the mock or the assertion.
        # The original test for _generate_research_plan parses the goal.
        # Let's ensure the mock provides a response that includes the goal.
        # The prompt to LLM in _generate_research_plan does not ask for "Research Goal:" explicitly in the output.
        # It seems the `goal` returned by `_generate_research_plan` is `natural_query` or a processed version.
        # The example in `_generate_research_plan` shows the LLM does not output "Research Goal:"
        # The function `_generate_research_plan` returns `natural_query` as the first element of the tuple.
        # So the assertion `self.assertEqual(goal, "Understand the applications of AI in healthcare.")` was likely
        # based on an older version or a misunderstanding of what `_generate_research_plan` returns as `goal`.
        # It should return the `natural_query` as `research_goal`.

        goal, queries = await _generate_research_plan(natural_query, mock_llm_client, max_queries)
        
        self.assertEqual(goal, natural_query) # `_generate_research_plan` returns `natural_query` as goal
        self.assertEqual(len(queries), 2)
        self.assertEqual(queries[0], ("AI diagnostics healthcare", "AI techniques for medical diagnosis."))
        self.assertEqual(queries[1], ("machine learning drug discovery", "ML in pharmaceutical research."))
        mock_llm_client.generate_text.assert_called_once()

    async def test_llm_client_error_in_plan_generation(self): # Renamed from test_gemini_client_error
        mock_llm_client = MagicMock()
        mock_llm_client.generate_text = MagicMock(side_effect=Exception("LLM API Error"))
        
        natural_query = "AI in healthcare"
        max_queries = 3
        
        goal, queries = await _generate_research_plan(natural_query, mock_llm_client, max_queries)
        
        # Fallback behavior of _generate_research_plan
        self.assertEqual(goal, natural_query) 
        self.assertEqual(len(queries), 1)
        self.assertEqual(queries[0], (natural_query, "Original query"))
        mock_llm_client.generate_text.assert_called_once()

    async def test_malformed_response_from_llm_in_plan_generation(self): # Renamed
        mock_llm_client = MagicMock()
        # Response that doesn't match the expected query line format
        mock_llm_client.generate_text = MagicMock(return_value=(
            "This is not the query format expected.\n"
            "No Query: lines here."
        ))
        
        natural_query = "AI in healthcare"
        max_queries = 1
        
        goal, queries = await _generate_research_plan(natural_query, mock_llm_client, max_queries)
        
        self.assertEqual(goal, natural_query) 
        self.assertEqual(len(queries), 1) # Fallback to original query due to parsing failure
        self.assertEqual(queries[0], (natural_query, "Original query"))
        mock_llm_client.generate_text.assert_called_once()

    # This test is similar to the one above, let's ensure it covers a slightly different malformed case
    async def test_malformed_response_no_queries_found_in_plan_generation(self): # Renamed
        mock_llm_client = MagicMock()
        mock_llm_client.generate_text = MagicMock(return_value=(
            "Search Queries:\n" # Correct start, but no actual query lines
            "Some other text but no lines starting with '1. Query: ...'"
        ))
        
        natural_query = "AI in healthcare"
        max_queries = 3
        
        goal, queries = await _generate_research_plan(natural_query, mock_llm_client, max_queries)
        
        self.assertEqual(goal, natural_query)
        self.assertEqual(len(queries), 1) # Fallback to original query
        self.assertEqual(queries[0], (natural_query, "Original query"))
        mock_llm_client.generate_text.assert_called_once()


class TestCalculateRelevanceScore(unittest.IsolatedAsyncioTestCase):
    async def test_successful_score_parsing(self):
        mock_llm_client = MagicMock() # Changed from mock_gemini_client
        mock_llm_client.generate_text = MagicMock(return_value="Score: 0.85 | Explanation: Highly relevant due to focus on NLP.")
        
        score, explanation = await _calculate_relevance_score(
            title="Test Paper", authors=["Auth A"], abstract="Test abstract",
            original_query="NLP applications", client=mock_llm_client # Pass mock_llm_client
        )
        
        self.assertEqual(score, 0.85)
        self.assertEqual(explanation, "Highly relevant due to focus on NLP.")
        mock_llm_client.generate_text.assert_called_once()

    async def test_score_parsing_variations(self):
        test_cases = [
            ("Score: 1.0 | Explanation: Perfect match.", 1.0, "Perfect match."),
            ("Score: 0.0 | Explanation: Not relevant.", 0.0, "Not relevant."),
            ("Score: 0.7 | Explanation: Somewhat relevant.", 0.7, "Somewhat relevant."),
            ("Score: 0 | Explanation: Not relevant (int score).", 0.0, "Not relevant (int score)."),
            ("Score: 1 | Explanation: Perfect match (int score).", 1.0, "Perfect match (int score)."),
        ]
        
        for response_str, expected_score, expected_explanation in test_cases:
            with self.subTest(response_str=response_str):
                mock_gemini_client = MagicMock(spec=GeminiClient)
                mock_gemini_client.generate_text = MagicMock(return_value=response_str)
                
                score, explanation = await _calculate_relevance_score(
                    title="Test", authors=[], abstract="Test", original_query="Test", client=mock_gemini_client
                )
                
                self.assertEqual(score, expected_score)
                self.assertEqual(explanation, expected_explanation)

    async def test_malformed_response_no_score_prefix(self):
        mock_gemini_client = MagicMock(spec=GeminiClient)
        mock_gemini_client.generate_text = MagicMock(return_value="This paper is good. Relevance: high")
        
        score, explanation = await _calculate_relevance_score(
            title="Test", authors=[], abstract="Test", original_query="Test", client=mock_gemini_client
        )
        
        self.assertEqual(score, 0.0) # Default score due to parsing failure
        self.assertEqual(explanation, "Could not parse score or explanation.") # Default explanation
        mock_gemini_client.generate_text.assert_called_once()

    async def test_malformed_response_different_format(self):
        mock_gemini_client = MagicMock(spec=GeminiClient)
        mock_gemini_client.generate_text = MagicMock(return_value="Relevance: 0.9, Reason: Very good paper")
        
        score, explanation = await _calculate_relevance_score(
            title="Test", authors=[], abstract="Test", original_query="Test", client=mock_gemini_client
        )
        
        self.assertEqual(score, 0.0) # Default score
        self.assertEqual(explanation, "Could not parse score or explanation.")
        mock_gemini_client.generate_text.assert_called_once()

    async def test_gemini_client_error_for_relevance(self):
        mock_gemini_client = MagicMock(spec=GeminiClient)
        mock_gemini_client.generate_text = MagicMock(side_effect=Exception("Gemini API Error"))
        
        score, explanation = await _calculate_relevance_score(
            title="Test", authors=[], abstract="Test", original_query="Test", client=mock_gemini_client
        )
        
        self.assertEqual(score, 0.0)
        self.assertEqual(explanation, "スコア計算エラー") # Error message from the function
        mock_gemini_client.generate_text.assert_called_once()


class TestDeduplicatePapers(unittest.TestCase):
    def test_no_duplicates(self):
        nodes = [
            QueryNode(query="q1", description="d1", paper_count=1, papers=[
                ScoredPaper(arxiv_id="1", title="P1", authors=[], abstract="", published_date=datetime.now(), url="", categories=[], relevance_score=1, relevance_explanation="")
            ]),
            QueryNode(query="q2", description="d2", paper_count=1, papers=[
                ScoredPaper(arxiv_id="2", title="P2", authors=[], abstract="", published_date=datetime.now(), url="", categories=[], relevance_score=1, relevance_explanation="")
            ])
        ]
        self.assertEqual(_deduplicate_papers(nodes), 2)

    def test_with_duplicates(self):
        paper1 = ScoredPaper(arxiv_id="1", title="P1", authors=[], abstract="", published_date=datetime.now(), url="", categories=[], relevance_score=1, relevance_explanation="")
        paper2 = ScoredPaper(arxiv_id="2", title="P2", authors=[], abstract="", published_date=datetime.now(), url="", categories=[], relevance_score=1, relevance_explanation="")
        nodes = [
            QueryNode(query="q1", description="d1", paper_count=2, papers=[paper1, paper2]),
            QueryNode(query="q2", description="d2", paper_count=1, papers=[paper1]) # Duplicate paper1
        ]
        self.assertEqual(_deduplicate_papers(nodes), 2)

    def test_with_multiple_duplicates_across_nodes(self):
        paper1 = ScoredPaper(arxiv_id="1", title="P1", authors=[], abstract="", published_date=datetime.now(), url="", categories=[], relevance_score=1, relevance_explanation="")
        paper2 = ScoredPaper(arxiv_id="2", title="P2", authors=[], abstract="", published_date=datetime.now(), url="", categories=[], relevance_score=1, relevance_explanation="")
        paper3 = ScoredPaper(arxiv_id="3", title="P3", authors=[], abstract="", published_date=datetime.now(), url="", categories=[], relevance_score=1, relevance_explanation="")
        nodes = [
            QueryNode(query="q1", description="d1", paper_count=2, papers=[paper1, paper2]),
            QueryNode(query="q2", description="d2", paper_count=2, papers=[paper1, paper3]),
            QueryNode(query="q3", description="d3", paper_count=2, papers=[paper2, paper3])
        ]
        self.assertEqual(_deduplicate_papers(nodes), 3)

    def test_empty_input(self):
        self.assertEqual(_deduplicate_papers([]), 0)

    def test_nodes_with_empty_papers_list(self):
        nodes = [
            QueryNode(query="q1", description="d1", paper_count=0, papers=[]),
            QueryNode(query="q2", description="d2", paper_count=0, papers=[])
        ]
        self.assertEqual(_deduplicate_papers(nodes), 0)


class TestResearchTreeSearch(unittest.IsolatedAsyncioTestCase):
    def _create_mock_arxiv_paper(self, arxiv_id: str, title: str, authors: List[str], abstract: str, year: int = 2023) -> MockArxivPaperSchema:
        return MockArxivPaperSchema(
            entry_id=f"http://arxiv.org/abs/{arxiv_id}",
            title=title,
            authors=[ArxivAuthor(name=name) for name in authors],
            summary=abstract,
            published=datetime(year, 1, 1),
            updated=datetime(year, 1, 1),
            pdf_url=f"http://arxiv.org/pdf/{arxiv_id}",
            categories=["cs.AI"]
        )

    @patch('backend.api.endpoints.research_tree._calculate_relevance_score', new_callable=AsyncMock)
    @patch('backend.api.endpoints.research_tree._generate_research_plan', new_callable=AsyncMock)
    async def test_successful_end_to_end_flow(
        self, 
        mock_generate_plan: AsyncMock, 
        mock_calculate_score: AsyncMock
    ):
        mock_gemini_client = MagicMock(spec=GeminiClient)
        mock_arxiv_client = MagicMock(spec=ArxivAPIClient)
        
        request = ResearchTreeRequest(natural_language_query="AI in education", max_results_per_query=1, max_queries=1)
        
        # Mock _generate_research_plan
        mock_generate_plan.return_value = ("Goal: AI education", [("query1", "desc1")])
        
        # Mock arxiv_client.search_papers
        paper1 = self._create_mock_arxiv_paper("2301.0001", "Paper 1", ["Auth X"], "Abstract 1")
        mock_arxiv_client.search_papers = AsyncMock(return_value=[paper1])
        
        # Mock _calculate_relevance_score
        mock_calculate_score.return_value = (0.9, "Very relevant")
        
        response = await research_tree_search(request, mock_gemini_client, mock_arxiv_client)
        
        self.assertIsInstance(response, SearchTreeResponse)
        self.assertEqual(response.original_query, request.natural_language_query)
        self.assertEqual(response.research_goal, "Goal: AI education")
        self.assertEqual(len(response.query_nodes), 1)
        
        node = response.query_nodes[0]
        self.assertEqual(node.query, "query1")
        self.assertEqual(node.description, "desc1")
        self.assertEqual(node.paper_count, 1)
        self.assertEqual(len(node.papers), 1)
        
        scored_paper = node.papers[0]
        self.assertEqual(scored_paper.title, "Paper 1")
        self.assertEqual(scored_paper.arxiv_id, "2301.0001")
        self.assertEqual(scored_paper.relevance_score, 0.9)
        self.assertEqual(scored_paper.relevance_explanation, "Very relevant")
        
        self.assertEqual(response.total_papers, 1)
        self.assertEqual(response.total_unique_papers, 1)

        mock_generate_plan.assert_called_once_with(request.natural_language_query, mock_gemini_client, request.max_queries)
        mock_arxiv_client.search_papers.assert_called_once_with(keyword="query1", max_results=request.max_results_per_query)
        mock_calculate_score.assert_called_once()


    @patch('backend.api.endpoints.research_tree._generate_research_plan', new_callable=AsyncMock)
    async def test_generate_research_plan_failure(self, mock_generate_plan: AsyncMock):
        mock_gemini_client = MagicMock(spec=GeminiClient)
        mock_arxiv_client = MagicMock(spec=ArxivAPIClient)
        request = ResearchTreeRequest(natural_language_query="test", max_results_per_query=1, max_queries=1)

        # Simulate _generate_research_plan raising an exception (as if Gemini client failed internally)
        # The function _generate_research_plan itself catches exceptions and returns a fallback.
        # So we test the fallback path of _generate_research_plan being reflected in research_tree_search
        mock_generate_plan.return_value = (f"Research on: {request.natural_language_query}", [(request.natural_language_query, "Original query")])
        
        # Mock arxiv and score calculation as they will still be called
        paper1 = self._create_mock_arxiv_paper("2301.0001", "Paper 1", ["Auth X"], "Abstract 1")
        mock_arxiv_client.search_papers = AsyncMock(return_value=[paper1])
        
        with patch('backend.api.endpoints.research_tree._calculate_relevance_score', new_callable=AsyncMock) as mock_calc_score:
            mock_calc_score.return_value = (0.5, "Relevant enough")
            response = await research_tree_search(request, mock_gemini_client, mock_arxiv_client)
            
            self.assertEqual(response.research_goal, f"Research on: {request.natural_language_query}")
            self.assertEqual(response.query_nodes[0].query, request.natural_language_query)
            self.assertEqual(response.query_nodes[0].description, "Original query")

    @patch('backend.api.endpoints.research_tree._calculate_relevance_score', new_callable=AsyncMock)
    @patch('backend.api.endpoints.research_tree._generate_research_plan', new_callable=AsyncMock)
    async def test_arxiv_search_failure_for_one_query(
        self, 
        mock_generate_plan: AsyncMock, 
        mock_calculate_score: AsyncMock
    ):
        mock_gemini_client = MagicMock(spec=GeminiClient)
        mock_arxiv_client = MagicMock(spec=ArxivAPIClient)
        request = ResearchTreeRequest(natural_language_query="multi-query test", max_results_per_query=1, max_queries=2)

        mock_generate_plan.return_value = ("Goal: MQ Test", [("query1_ok", "desc1"), ("query2_fail", "desc2")])
        
        paper_ok = self._create_mock_arxiv_paper("2301.0001", "OK Paper", ["Auth A"], "Abstract OK")

        async def mock_search_papers_side_effect(keyword, max_results):
            if keyword == "query1_ok":
                return [paper_ok]
            elif keyword == "query2_fail":
                raise Exception("Arxiv API down for this query")
            return []
        
        mock_arxiv_client.search_papers = AsyncMock(side_effect=mock_search_papers_side_effect)
        mock_calculate_score.return_value = (0.8, "Relevant")

        response = await research_tree_search(request, mock_gemini_client, mock_arxiv_client)

        self.assertEqual(len(response.query_nodes), 2)
        
        node1 = response.query_nodes[0]
        self.assertEqual(node1.query, "query1_ok")
        self.assertEqual(node1.paper_count, 1)
        self.assertEqual(len(node1.papers), 1)
        self.assertEqual(node1.papers[0].title, "OK Paper")
        
        node2 = response.query_nodes[1]
        self.assertEqual(node2.query, "query2_fail")
        self.assertEqual(node2.paper_count, 0) # Error during search results in empty list
        self.assertEqual(len(node2.papers), 0)
        
        self.assertEqual(response.total_papers, 1)
        self.assertEqual(response.total_unique_papers, 1)
        self.assertEqual(mock_arxiv_client.search_papers.call_count, 2)


    @patch('backend.api.endpoints.research_tree._calculate_relevance_score', new_callable=AsyncMock)
    @patch('backend.api.endpoints.research_tree._generate_research_plan', new_callable=AsyncMock)
    async def test_score_calculation_failure_for_one_paper(
        self, 
        mock_generate_plan: AsyncMock, 
        mock_calculate_score: AsyncMock
    ):
        mock_gemini_client = MagicMock(spec=GeminiClient)
        mock_arxiv_client = MagicMock(spec=ArxivAPIClient)
        request = ResearchTreeRequest(natural_language_query="score fail test", max_results_per_query=2, max_queries=1)

        mock_generate_plan.return_value = ("Goal: Score Test", [("query1", "desc1")])
        
        paper1 = self._create_mock_arxiv_paper("2301.0001", "Paper 1 Good Score", ["Auth A"], "Abstract 1")
        paper2 = self._create_mock_arxiv_paper("2301.0002", "Paper 2 Bad Score", ["Auth B"], "Abstract 2")
        mock_arxiv_client.search_papers = AsyncMock(return_value=[paper1, paper2])

        async def mock_score_side_effect(title, authors, abstract, original_query, client):
            if title == "Paper 1 Good Score":
                return (0.9, "Very relevant")
            elif title == "Paper 2 Bad Score":
                return (0.0, "スコア計算エラー") # Simulate error during scoring this paper
            return (0.1, "Fallback score")

        mock_calculate_score.side_effect = mock_score_side_effect
        
        response = await research_tree_search(request, mock_gemini_client, mock_arxiv_client)
        
        self.assertEqual(len(response.query_nodes[0].papers), 2)
        
        scored_paper1 = response.query_nodes[0].papers[0] # Assuming sort puts higher score first
        scored_paper2 = response.query_nodes[0].papers[1]

        # Check which paper is which based on title, as order might change after sorting
        if scored_paper1.title == "Paper 1 Good Score":
            good_paper_response = scored_paper1
            bad_paper_response = scored_paper2
        else:
            good_paper_response = scored_paper2
            bad_paper_response = scored_paper1

        self.assertEqual(good_paper_response.title, "Paper 1 Good Score")
        self.assertEqual(good_paper_response.relevance_score, 0.9)
        self.assertEqual(good_paper_response.relevance_explanation, "Very relevant")
        
        self.assertEqual(bad_paper_response.title, "Paper 2 Bad Score")
        self.assertEqual(bad_paper_response.relevance_score, 0.0)
        self.assertEqual(bad_paper_response.relevance_explanation, "スコア計算エラー")
        
        self.assertEqual(mock_calculate_score.call_count, 2)

    async def test_overall_exception_handling_http_exception(self):
        mock_gemini_client = MagicMock(spec=GeminiClient)
        mock_arxiv_client = MagicMock(spec=ArxivAPIClient)
        request = ResearchTreeRequest(natural_language_query="test", max_results_per_query=1, max_queries=1)

        # Make _generate_research_plan raise an unexpected error
        with patch('backend.api.endpoints.research_tree._generate_research_plan', new_callable=AsyncMock) as mock_gen_plan:
            mock_gen_plan.side_effect = Exception("Unexpected major failure")
            
            with self.assertRaises(HTTPException) as context:
                await research_tree_search(request, mock_gemini_client, mock_arxiv_client)
            
            self.assertEqual(context.exception.status_code, 500)
            self.assertTrue("Research tree search failed: Unexpected major failure" in str(context.exception.detail))


if __name__ == '__main__':
    unittest.main()
