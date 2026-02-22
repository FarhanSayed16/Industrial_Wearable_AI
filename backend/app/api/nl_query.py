"""
Natural Language Query Endpoint (Innovation/Differentiator Feature)
Parses highly structured plain-text questions into deterministic SQLAlchemy queries.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from pydantic import BaseModel
from typing import Dict, Any
import datetime

from app.database import get_db
from app.models.worker import Worker
from app.models.session import Session
from app.models.activity_event import ActivityEvent

router = APIRouter()

class NLQueryRequest(BaseModel):
    query: str

class NLQueryResponse(BaseModel):
    answer: str

@router.post("/nl-query", response_model=NLQueryResponse)
async def process_natural_language_query(
    request: NLQueryRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    A rule-based NLP parser. For a production system, this could be swapped out 
    with a call to an LLM (OpenAI/Claude) using LangChain's SQLAgent.
    """
    q = request.query.lower()
    
    try:
        if "highest risk" in q or "most at risk" in q:
            # Query the worker with the highest current fatigue_score
            stmt = select(Worker).order_by(Worker.fatigue_score.desc()).limit(1)
            result = await db.execute(stmt)
            worker = result.scalar_one_or_none()
            if worker:
                return NLQueryResponse(answer=f"The worker with the highest current risk is {worker.name} with a fatigue score of {worker.fatigue_score:.2f}%.")
            return NLQueryResponse(answer="I couldn't find any worker risk data.")
            
        elif "idle" in q:
            # How many workers are currently idle?
            stmt = select(func.count(Worker.id)).where(Worker.state == 'idle')
            result = await db.execute(stmt)
            count = result.scalar()
            return NLQueryResponse(answer=f"There are currently {count} workers in an 'idle' state.")
            
        elif "active" in q or "sewing" in q:
            stmt = select(func.count(Worker.id)).where(Worker.state == 'sewing')
            result = await db.execute(stmt)
            count = result.scalar()
            return NLQueryResponse(answer=f"There are currently {count} workers actively 'sewing'.")
            
        elif "efficiency" in q or "productivity" in q:
            stmt = select(func.avg(Worker.productivity_score))
            result = await db.execute(stmt)
            avg_prod = result.scalar() or 0.0
            return NLQueryResponse(answer=f"The average productivity score across the factory floor is {avg_prod:.1f}%.")
            
        else:
            return NLQueryResponse(
                answer="I can answer questions like: 'Who is at highest risk?', 'How many workers are idle?', or 'What is the average productivity?'"
            )
            
    except Exception as e:
        return NLQueryResponse(answer=f"Sorry, I encountered an error pulling that data: {str(e)}")
