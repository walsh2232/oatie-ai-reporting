from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class TableMetadata(Base):
    """
    ORM model for storing table metadata in the database.
    Each row represents a table that exists in a specific schema.
    """
    __tablename__ = "table_metadata"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    schema_name = Column(String(100), nullable=False, index=True)
    table_name = Column(String(200), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Composite index for efficient lookups
    __table_args__ = (
        Index('ix_schema_table', 'schema_name', 'table_name'),
    )
    
    def __repr__(self):
        return f"<TableMetadata(schema='{self.schema_name}', table='{self.table_name}')>"
