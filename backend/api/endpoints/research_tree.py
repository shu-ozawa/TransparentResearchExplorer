from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import logging
import re
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from fastapi.responses import StreamingResponse
import asyncio
import json

from backend.app.dependencies import get_llm_client
from backend.app.clients.gemini_client import GeminiClient # For type hinting
from backend.app.clients.ollama_client import OllamaClient # For type hinting
from backend.api.arxiv_client import ArxivAPIClient, get_arxiv_client

router = APIRouter()
logger = logging.getLogger(__name__)

# === Input Models ===
class ResearchTreeRequest(BaseModel):
    natural_language_query: str
    max_results_per_query: int = 5
    max_queries: int = 5

# === Output Models ===
class ScoredPaper(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    published_date: datetime
    url: str
    categories: List[str]
    arxiv_id: str
    relevance_score: float
    relevance_explanation: str

class QueryNode(BaseModel):
    """個別のクエリとその結果を表すノード"""
    query: str
    description: str  # このクエリが何を探すためのものか
    papers: List[ScoredPaper]
    paper_count: int

class SearchTreeResponse(BaseModel):
    """ツリー構造の検索結果"""
    original_query: str
    research_goal: str  # Geminiが解釈した研究目標
    query_nodes: List[QueryNode]
    total_papers: int
    total_unique_papers: int  # 重複除去後の論文数

# === Helper Functions ===
async def _generate_research_plan(natural_query: str, client: Union[GeminiClient, OllamaClient], max_queries: int) -> tuple[str, List[tuple[str, str]]]:
    """
    自然言語クエリから研究目標と複数の検索クエリを生成
    Returns: (research_goal, [(query, description), ...])
    """
    prompt = (
        f"You are a research assistant. Your task is to break down the following research topic into a list of specific search queries for academic paper databases.\n\n"
        f"Please generate up to {max_queries} distinct search queries, each exploring a different facet or angle of the research topic. Each query should be designed to find relevant academic papers and should be accompanied by a brief description of its focus.\n"
        f"IMPORTANT: Always generate search queries in English, even if the research topic is in another language. This is crucial for searching academic papers.\n\n"
        f"---\n"
        f"Additional Instructions:\n"
        f"- Always include general and representative keywords related to the topic (e.g., 'machine learning', 'deep learning', 'LLM', etc.) in your queries, even if the topic is specific.\n"
        f"- Combine multiple general terms using OR to broaden the search and ensure that each query will likely return more than 10 papers.\n"
        f"- Prioritize query design that will result in a large number of hits, rather than being too specific.\n"
        f"- Assume that the user will read the most recent papers first, so queries should not be limited by publication year.\n"
        f"---\n\n"
        f"Format your response EXACTLY as follows, including the numbering for queries:\n"
        f"Search Queries:\n"
        f"1. Query: [search terms 1 in English] | Description: [description for query 1]\n"
        f"2. Query: [search terms 2 in English] | Description: [description for query 2]\n"
        f"...\n\n"
        f"For example:\n\n"
        f"Research Topic: Explore the benefits and challenges of using TypeScript in large-scale front-end applications.\n"
        f"Search Queries:\n"
        f"1. Query: \"TypeScript large-scale applications benefits\" OR \"enterprise TypeScript advantages\" | Description: Focuses on the general benefits and advantages of using TypeScript in developing large front-end applications.\n"
        f"2. Query: \"TypeScript challenges large projects\" OR \"TypeScript adoption hurdles enterprise\" | Description: Investigates the difficulties and obstacles encountered when implementing TypeScript in substantial or enterprise-level projects.\n"
        f"3. Query: \"TypeScript performance impact large frontend\" OR \"TypeScript scalability front-end metrics\" | Description: Examines the performance implications and scalability aspects of TypeScript in the context of large-scale front-end development.\n\n"
        f"Research Topic: The impact of renewable energy sources on grid stability.\n"
        f"Search Queries:\n"
        f"1. Query: \"renewable energy\" OR \"grid stability\" OR \"intermittent renewables\" | Description: Identifies challenges and issues related to integrating renewable energy sources into the power grid due to their intermittent nature.\n"
        f"2. Query: \"grid stability solutions\" OR \"renewable energy\" OR \"mitigation techniques\" | Description: Explores solutions and techniques to maintain grid stability while incorporating a high penetration of renewable energy sources.\n\n"
        f"Now, please provide the search queries for the following research topic:\n"
        f"Research Topic: {natural_query}\n"
    )
    
    try:
        # Both clients now support a model parameter with a default, so just passing prompt is fine.
        response = client.generate_text(prompt=prompt) 
        # logger.info(f"Raw LLM Response: {repr(response)}")

        # Pre-process the response string for robustness
        processed_response = response.replace('\r\n', '\n').replace('\r', '\n')
        processed_response = processed_response.strip()
        logger.info(f"Processed LLM Response for Parsing: {repr(processed_response)}")
        
        # クエリを抽出
        queries = []
        # Look for lines starting with "X. Query: " and containing " | Description: "
        query_pattern = r"^\d+\.\s*Query:\s*(.+?)\s*\|\s*Description:\s*(.+?)$"
        query_matches = re.findall(query_pattern, processed_response, re.MULTILINE)
        
        for query_text, description in query_matches:
            queries.append((query_text.strip(), description.strip()))
        
        if not queries:
            # Use processed_response in warning for consistency if parsing fails
            logger.warning(f"Could not parse any Search Queries from processed response: {processed_response}. Using original query as fallback.")
            queries = [(natural_query, "Original query")]
        
        return natural_query, queries[:max_queries]
        
    except Exception as e:
        logger.error(f"Error generating research plan: {e}")
        return natural_query, [(natural_query, "Original query")]

async def _calculate_relevance_score(
    title: str,
    authors: List[str],
    abstract: str,
    original_query: str,
    client: Union[GeminiClient, OllamaClient]
) -> tuple[float, str]:
    """
    論文と元の自然言語クエリの関連性スコアと説明を計算
    """
    prompt = (
        f"Rate the relevance of this research paper to the original research question on a scale of 0.0 to 1.0 "
        f"(0.0 = not relevant, 1.0 = highly relevant). Provide a brief explanation for your rating.\n\n"
        f"Paper Title: {title}\n"
        f"Authors: {', '.join(authors)}\n"
        f"Abstract (first 500 chars): {abstract[:500]}...\n\n"
        f"Original Research Question: {original_query}\n\n"
        f"Format your response EXACTLY as follows: Score: [score as a float between 0.0 and 1.0] | Explanation: [your brief reason here]"
    )
    
    try:
        # Both clients now support a model parameter with a default.
        response = client.generate_text(prompt=prompt)
        
        score = 0.0
        explanation = "Could not parse score or explanation."

        # Look for "Score: " followed by a float and " | Explanation: " followed by text
        match = re.search(r"Score:\s*(\d+\.?\d*)\s*\|\s*Explanation:\s*(.+)", response, re.IGNORECASE)
        
        if match:
            try:
                score = float(match.group(1))
                score = max(0.0, min(1.0, score)) # Ensure score is within 0.0-1.0
                explanation = match.group(2).strip()
            except ValueError:
                logger.error(f"Could not parse score as float from response: {response}")
                score = 0.0 # Default score on parsing error
                explanation = "Error parsing score value."
            except IndexError:
                logger.error(f"Could not parse explanation from response: {response}")
                explanation = "Error parsing explanation." # Default explanation
        else:
            logger.warning(f"Could not parse relevance score and explanation using strict format from response: {response}")
            # Attempt to extract score if possible, even if format is slightly off, as a lenient fallback.
            score_match_fallback = re.search(r"Score:\s*(\d+\.?\d*)", response, re.IGNORECASE)
            if score_match_fallback:
                try:
                    score = float(score_match_fallback.group(1))
                    score = max(0.0, min(1.0, score))
                    explanation = "Explanation not parsed due to format mismatch."
                except ValueError:
                    score = 0.0
                    explanation = "Could not parse score (fallback attempt failed)."
            else:
                # If no score found at all, keep defaults
                pass


        return score, explanation
        
    except Exception as e:
        logger.error(f"Error calculating relevance score: {e}")
        return 0.0, "スコア計算エラー"

def _deduplicate_papers(query_nodes: List[QueryNode]) -> int:
    """
    重複論文を数えて、ユニークな論文数を返す
    """
    seen_ids = set()
    for node in query_nodes:
        for paper in node.papers:
            seen_ids.add(paper.arxiv_id)
    return len(seen_ids)

# === Main Endpoint ===
@router.post("/research-tree", response_model=SearchTreeResponse, summary="Multi-query research with tree visualization")
async def research_tree_search(
    request: ResearchTreeRequest,
    llm_client: Union[GeminiClient, OllamaClient] = Depends(get_llm_client),
    arxiv_client: ArxivAPIClient = Depends(get_arxiv_client)
):
    """
    自然言語クエリから複数の検索戦略を生成し、ツリー構造で結果を返却
    
    フロー:
    1. 自然言語クエリ → Geminiが研究目標と複数クエリ生成
    2. 各クエリでarXiv検索
    3. 各論文に元の自然言語クエリとの関連性スコア計算
    4. ツリー構造で返却（フロントエンド可視化用）
    """
    try:
        # Step 1: 研究計画生成（目標 + 複数クエリ）
        logger.info(f"Generating research plan for: {request.natural_language_query}")
        research_goal, query_plans = await _generate_research_plan(
            request.natural_language_query,
            llm_client,
            request.max_queries
        )
        logger.info(f"Research goal: {research_goal}")
        logger.info(f"Generated {len(query_plans)} queries")
        
        # Step 2: 各クエリで検索実行
        query_nodes = []
        total_papers = 0
        
        for query_text, description in query_plans:
            logger.info(f"Searching with query: {query_text}")
            
            try:
                # arXiv検索
                arxiv_results = await arxiv_client.search_papers(
                    keyword=query_text,
                    max_results=request.max_results_per_query
                )
                
                # 各論文にスコア付与
                scored_papers = []
                for result in arxiv_results:
                    authors = [author.name for author in result.authors]
                    
                    # 関連性スコア計算（元の自然言語クエリに対して）
                    score, explanation = await _calculate_relevance_score(
                        title=result.title,
                        authors=authors,
                        abstract=result.summary or "",
                        original_query=request.natural_language_query,
                        client=llm_client
                    )
                    
                    scored_paper = ScoredPaper(
                        title=result.title,
                        authors=authors,
                        abstract=result.summary or "",
                        published_date=result.published,
                        url=result.pdf_url,
                        categories=result.categories,
                        arxiv_id=result.entry_id.split('/')[-1],  # arXiv IDを抽出
                        relevance_score=score,
                        relevance_explanation=explanation
                    )
                    scored_papers.append(scored_paper)
                
                # スコア順でソート
                scored_papers.sort(key=lambda x: x.relevance_score, reverse=True)
                
                # QueryNodeを作成
                query_node = QueryNode(
                    query=query_text,
                    description=description,
                    papers=scored_papers,
                    paper_count=len(scored_papers)
                )
                query_nodes.append(query_node)
                total_papers += len(scored_papers)
                
            except Exception as e:
                logger.error(f"Error searching with query '{query_text}': {e}")
                # エラーが発生したクエリも空のノードとして追加
                query_nodes.append(QueryNode(
                    query=query_text,
                    description=description,
                    papers=[],
                    paper_count=0
                ))
        
        # Step 3: 重複論文数を計算
        unique_papers_count = _deduplicate_papers(query_nodes)
        
        return SearchTreeResponse(
            original_query=request.natural_language_query,
            research_goal=research_goal,
            query_nodes=query_nodes,
            total_papers=total_papers,
            total_unique_papers=unique_papers_count
        )
        
    except Exception as e:
        logger.error(f"Error in research tree search: {e}")
        raise HTTPException(status_code=500, detail=f"Research tree search failed: {str(e)}")

@router.post("/research-tree/stream", summary="Multi-query research with streaming response")
async def research_tree_stream(
    request: ResearchTreeRequest,
    llm_client: Union[GeminiClient, OllamaClient] = Depends(get_llm_client),
    arxiv_client: ArxivAPIClient = Depends(get_arxiv_client)
):
    """
    クエリ生成→即返却→各クエリごとに論文検索→都度返却（ストリーミング）
    """
    async def event_stream():
        # Step 1: クエリ生成
        research_goal, query_plans = await _generate_research_plan(
            request.natural_language_query,
            llm_client,
            request.max_queries
        )
        # クエリ生成結果をまず送信
        yield f"data: {json.dumps({'type': 'queries', 'original_query': request.natural_language_query, 'research_goal': research_goal, 'queries': [{'query': q, 'description': d} for q, d in query_plans]})}\n\n"
        await asyncio.sleep(0.05)

        # Step 2: 各クエリで検索実行
        for query_text, description in query_plans:
            try:
                arxiv_results = await arxiv_client.search_papers(
                    keyword=query_text,
                    max_results=request.max_results_per_query
                )
                scored_papers = []
                for result in arxiv_results:
                    authors = [author.name for author in result.authors]
                    score, explanation = await _calculate_relevance_score(
                        title=result.title,
                        authors=authors,
                        abstract=result.summary or "",
                        original_query=request.natural_language_query,
                        client=llm_client
                    )
                    scored_paper = {
                        'title': result.title,
                        'authors': authors,
                        'abstract': result.summary or "",
                        'published_date': result.published.isoformat() if hasattr(result.published, 'isoformat') else str(result.published),
                        'url': result.pdf_url,
                        'categories': result.categories,
                        'arxiv_id': result.entry_id.split('/')[-1],
                        'relevance_score': score,
                        'relevance_explanation': explanation
                    }
                    scored_papers.append(scored_paper)
                scored_papers.sort(key=lambda x: x['relevance_score'], reverse=True)
                # クエリごとの論文リストを送信
                yield f"data: {json.dumps({'type': 'papers', 'query': query_text, 'description': description, 'papers': scored_papers})}\n\n"
                await asyncio.sleep(0.05)
            except Exception as e:
                # エラー時も空リストで送信
                yield f"data: {json.dumps({'type': 'papers', 'query': query_text, 'description': description, 'papers': [], 'error': str(e)})}\n\n"
                await asyncio.sleep(0.05)

    return StreamingResponse(event_stream(), media_type="text/event-stream")

# === Optional: 統計情報取得エンドポイント ===
@router.get("/research-stats", summary="Get research statistics")
async def get_research_stats(
    # 将来的にキャッシュされた検索結果の統計を返すなど
):
    """研究統計情報を取得（将来の拡張用）"""
    return {"message": "Statistics endpoint - coming soon"}
