from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from . import service
from db.database import async_session
from db.models import Players
from db.schemas import PlayerBase, PlayerResponse
from ..rate_limiter import limiter
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/games",
    tags=["games"],
    responses={404: {"description": "Not found"}},
)

@router.get("/standings")
@limiter.limit("10/minute")
async def get_standings(request: Request, conference: str = 'Overall', season: str = '2025-26'):
    standings = await service.get_standings(season=season, conference=conference)
    return standings

