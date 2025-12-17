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
    prefix="/players",
    tags=["players"],
    responses={404: {"description": "Not found"}},
)

@router.get("/all", response_model=List[PlayerResponse])
@limiter.limit("10/minute")
async def get_all_players(request: Request, db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    players = await service.get_players_from_db(db=db, skip=skip, limit=limit)
    return [PlayerResponse.model_validate(player) for player in players]

@router.get("/{player_id}")
@limiter.limit("10/minute")
async def get_player_by_id(request: Request, player_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_player_by_id(db=db, player_id=player_id)

@router.get("/search/{name}")
@limiter.limit("10/minute")
async def get_player_by_name(request: Request, name: str, db: AsyncSession = Depends(get_db)):
    return await service.get_player_by_name(db=db, name=name)