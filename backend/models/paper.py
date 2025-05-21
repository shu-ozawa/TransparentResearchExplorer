from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from backend.core.database import Base

class Paper(Base):
    __tablename__ = "papers_cache"

    id = Column(Integer, primary_key=True, index=True)
    arxiv_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    authors = Column(JSON) # Storing as JSON
    abstract = Column(Text, nullable=True)
    published_date = Column(DateTime, nullable=True)
    url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Paper(id={self.id}, arxiv_id='{self.arxiv_id}', title='{self.title[:30]}...')>"
