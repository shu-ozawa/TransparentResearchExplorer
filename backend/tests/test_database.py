import pytest
from sqlalchemy import create_engine, StaticPool, text # Added text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient # Though not strictly for DB, good for context if we test endpoints later
import os

# Adjust import paths if necessary. This assumes 'backend' is a package available in PYTHONPATH.
# For tests, it's common to adjust PYTHONPATH or use relative imports carefully.
from backend.core.database import Base, get_db
from backend.models.paper import Paper
from backend.app.main import app # To potentially override dependency later

# Use an in-memory SQLite database for testing
# DATABASE_URL_TEST = "sqlite:///:memory:" # Standard in-memory
# For this test, we'll use a file-based SQLite DB to ensure create_all works and persists for inspection if needed,
# then clean it up. Or use StaticPool for true in-memory that works with TestClient's multiple threads/sessions.
DATABASE_URL_TEST = "sqlite:///./test_tre_cache.db"

engine_test = create_engine(
    DATABASE_URL_TEST,
    # connect_args={"check_same_thread": False}, # Not needed with StaticPool
    poolclass=StaticPool, # Recommended for SQLite in-memory with TestClient
)
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# Override the get_db dependency for testing
def override_get_db():
    try:
        db = SessionTesting()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Fixture to create tables for each test function and clean up
@pytest.fixture(scope="function")
def db_session():
    # Create tables
    Base.metadata.create_all(bind=engine_test)
    db = SessionTesting()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine_test)
        # If using a file-based test DB and want to clean it up:
        # if os.path.exists("./test_tre_cache.db"):
        #     os.remove("./test_tre_cache.db")


def test_database_connection(db_session: Session):
    # Simple query to check connection
    result = db_session.execute(text("SELECT 1")).scalar_one()
    assert result == 1

def test_paper_table_creation(db_session: Session):
    # Check if the 'papers_cache' table exists in the metadata
    assert "papers_cache" in Base.metadata.tables
    # You could also query sqlite_master for table names if needed,
    # but checking Base.metadata is more SQLAlchemy idiomatic for created tables.

def test_create_and_read_paper(db_session: Session):
    # Create a new paper instance
    paper_data = {
        "arxiv_id": "2301.12345v1",
        "title": "Test Paper for TRE",
        "authors": ["Author A", "Author B"],
        "abstract": "This is an abstract for the test paper.",
        "url": "http://arxiv.org/abs/2301.12345v1",
        # published_date can be added if needed
    }
    new_paper = Paper(**paper_data)
    
    db_session.add(new_paper)
    db_session.commit()
    db_session.refresh(new_paper)
    
    assert new_paper.id is not None
    assert new_paper.arxiv_id == "2301.12345v1"
    assert new_paper.title == "Test Paper for TRE"
    
    # Read the paper back from the database
    retrieved_paper = db_session.query(Paper).filter(Paper.arxiv_id == "2301.12345v1").first()
    
    assert retrieved_paper is not None
    assert retrieved_paper.id == new_paper.id
    assert retrieved_paper.title == "Test Paper for TRE"
    assert retrieved_paper.authors == ["Author A", "Author B"]

def test_paper_arxiv_id_unique_constraint(db_session: Session):
    paper1_data = {
        "arxiv_id": "common.00001",
        "title": "First Paper",
    }
    paper1 = Paper(**paper1_data)
    db_session.add(paper1)
    db_session.commit()

    paper2_data = {
        "arxiv_id": "common.00001", # Same arxiv_id
        "title": "Second Paper with Same Arxiv ID",
    }
    paper2 = Paper(**paper2_data)
    db_session.add(paper2)
    
    with pytest.raises(Exception) as excinfo: # Catches IntegrityError from SQLAlchemy/DB driver
        db_session.commit()
    # The specific exception type might be IntegrityError from sqlalchemy.exc
    # For SQLite, this is often sqlite3.IntegrityError wrapped by SQLAlchemy
    # Adjusted assertion to be more direct for SQLite's error message
    assert "unique constraint failed" in str(excinfo.value).lower()

# It's good practice to also have a TestClient fixture if you plan to test FastAPI endpoints
# that interact with the database.
# @pytest.fixture(scope="module")
# def client():
#     # Setup any test-specific app configurations if needed
#     Base.metadata.create_all(bind=engine_test) # Ensure tables are created for the module scope if needed
#     client = TestClient(app)
#     yield client
#     Base.metadata.drop_all(bind=engine_test) # Clean up tables
#     if os.path.exists("./test_tre_cache.db"):
#         os.remove("./test_tre_cache.db")
