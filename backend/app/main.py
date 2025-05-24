from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.database import engine, Base, create_db_and_tables # Updated import
from backend.api.endpoints import arxiv as arxiv_router  # Import the arxiv router
from backend.api.endpoints import queries as queries_router  # Import the queries router
from backend.api.endpoints import papers as papers_router  # Import the papers router

# If Paper model is needed in main.py for some reason, import it like:
# from backend.models.paper import Paper

# Create database tables on startup
# This is a simple way for prototypes. For production, you might use Alembic migrations.
create_db_and_tables()

app = FastAPI(
    title="Transparent Research Explorer API",
    description="API for searching arXiv and processing research papers.",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

# Include routers
app.include_router(arxiv_router.router, prefix="/api/arxiv", tags=["arXiv"])
app.include_router(queries_router.router, prefix="/api/queries", tags=["Queries"])
app.include_router(papers_router.router, prefix="/api/papers", tags=["Papers"])

# Example of how to ensure tables are created using an event handler
# This is often preferred over calling create_db_and_tables() directly at the module level,
# especially in more complex applications or when using app factories.
# @app.on_event("startup")
# async def startup_event():
#     create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Hello World from Transparent Research Explorer Backend"}

# Example endpoint to test DB (Optional - can be removed later)
# from fastapi import Depends
# from sqlalchemy.orm import Session
# from backend.core.database import get_db
# from backend.models.paper import Paper

# @app.post("/add_dummy_paper/")
# def add_dummy_paper(db: Session = Depends(get_db)):
#     dummy_paper = Paper(
#         arxiv_id="1234.56789",
#         title="A Dummy Paper for Testing",
#         authors=["Author One", "Author Two"],
#         abstract="This is a test paper abstract.",
#         url="http://example.com/paper/1234.56789"
#     )
#     db.add(dummy_paper)
#     db.commit()
#     db.refresh(dummy_paper)
#     return dummy_paper
