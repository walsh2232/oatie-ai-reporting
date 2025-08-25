from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import structlog
import time

from app.db.database import get_db
from app.models.models import AIInteraction
from app.schemas.ai import AIQueryRequest, AIQueryResponse

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/query", response_model=AIQueryResponse)
async def process_ai_query(request: AIQueryRequest, db: Session = Depends(get_db)):
    """Process AI query for Oracle BI Publisher report generation"""
    start_time = time.time()
    
    try:
        # TODO: Implement actual AI processing logic
        # This is a placeholder for the AI query processing
        mock_response = {
            "response": f"Based on your query '{request.query}', I suggest creating a report that analyzes {request.context or 'the requested data'}.",
            "sql_query": "SELECT * FROM sample_table WHERE condition = 'example';",
            "suggested_report_name": f"AI Generated Report - {request.query[:50]}",
            "confidence": 0.85
        }
        
        # Record interaction
        processing_time = int((time.time() - start_time) * 1000)
        interaction = AIInteraction(
            user_query=request.query,
            ai_response=mock_response["response"],
            sql_generated=mock_response["sql_query"],
            session_id=request.session_id,
            processing_time=processing_time,
            is_successful=True
        )
        db.add(interaction)
        db.commit()
        
        logger.info(
            "AI query processed",
            session_id=request.session_id,
            processing_time=processing_time,
            query_length=len(request.query)
        )
        
        return AIQueryResponse(**mock_response)
        
    except Exception as e:
        logger.error("AI query processing failed", error=str(e), session_id=request.session_id)
        
        # Record failed interaction
        processing_time = int((time.time() - start_time) * 1000)
        interaction = AIInteraction(
            user_query=request.query,
            ai_response="Error processing query",
            session_id=request.session_id,
            processing_time=processing_time,
            is_successful=False
        )
        db.add(interaction)
        db.commit()
        
        raise HTTPException(status_code=500, detail="Failed to process AI query")


@router.get("/interactions/{session_id}")
async def get_session_interactions(session_id: str, db: Session = Depends(get_db)):
    """Get AI interactions for a session"""
    try:
        interactions = db.query(AIInteraction).filter(
            AIInteraction.session_id == session_id
        ).order_by(AIInteraction.created_at.desc()).limit(50).all()
        
        return {
            "session_id": session_id,
            "interactions": interactions,
            "total_count": len(interactions)
        }
    except Exception as e:
        logger.error("Failed to fetch interactions", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch interactions")