from fastapi import FastAPI
from backend.core.database import engine, Base, create_db_and_tables # Updated import
# If Paper model is needed in main.py for some reason, import it like:
# from backend.models.paper import Paper 

# Create database tables on startup
# This is a simple way for prototypes. For production, you might use Alembic migrations.
create_db_and_tables() 

app = FastAPI()

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
