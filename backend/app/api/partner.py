"""
Public-facing B2B REST API for Partners (e.g. ERP integrations).
Versioned at /api/v1. Secured via static API Keys instead of Dashboard JWTs.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timedelta
import os

from app.database import get_db
from app.models.worker import Worker
from app.models.session import Session
from app.schemas import WorkerResponse, SessionResponse

router = APIRouter()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

EXPECTED_API_KEY = os.getenv("PARTNER_API_KEY", "b2b-test-key-999")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=403, detail="Could not validate API KEY"
        )
    return api_key_header


@router.get("/workers", response_model=List[WorkerResponse])
async def get_workers(
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """Retrieve all workers."""
    result = await db.execute(select(Worker))
    return result.scalars().all()


@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """Retrieve recent manufacturing sessions."""
    result = await db.execute(
        select(Session).order_by(Session.started_at.desc()).limit(limit)
    )
    return result.scalars().all()
