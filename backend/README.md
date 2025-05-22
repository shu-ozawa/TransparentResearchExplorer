# Transparent Research Explorer Backend

This is the backend service for the Transparent Research Explorer application. It provides API endpoints for querying arXiv papers and generating related search queries using the Gemini AI.

## Setup Instructions

### 1. Create a new Conda environment
```bash
conda create -n tre-api python=3.12 -y
conda activate tre-api
```

### 2. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the `backend` directory with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

### 4. Run the server
```bash
uvicorn app.main:app --reload
```

The backend server will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Query Generation
- **POST /api/queries/generate**: Generate related queries from initial keywords using the Gemini API.

Request body example:
```json
{
  "initial_keywords": "machine learning in healthcare"
}
```

Response example:
```json
{
  "original_query": "machine learning in healthcare",
  "related_queries": [
    {
      "query": "deep learning for medical image analysis",
      "description": "Focuses on using deep learning techniques to analyze medical images like MRI or CT scans."
    },
    {
      "query": "reinforcement learning in personalized medicine",
      "description": "Explores applications of reinforcement learning for creating personalized treatment plans."
    }
  ]
}
```

### arXiv Search
- **POST /api/arxiv/search**: Search for papers on arXiv using keywords.
- **GET /api/arxiv/search**: Search for papers with query parameters.

## Development Notes

This project uses FastAPI for the web framework and SQLAlchemy for database operations. The Gemini API client is used to generate related search queries, and the arXiv API client is used for searching academic papers.
