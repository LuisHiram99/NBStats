from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from . import service
from db.database import async_session
from db.models import Teams
from db.schemas import TeamResponse
from ..rate_limiter import limiter
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}},
)


@router.get("/all", response_model=List[TeamResponse])
@limiter.limit("10/minute")
async def get_all_teams(request: Request, db: AsyncSession = Depends(get_db)):
    teams = await service.get_teams_from_db(db=db)
    return [TeamResponse.model_validate(team) for team in teams]


@router.get("/{abbrev}")
async def get_team_by_abbreviation(request: Request, abbrev: str, db: AsyncSession = Depends(get_db)):
    return await service.get_team_by_abbreviation(db=db, abbrev=abbrev)

@router.get("/conference/{conference}")
async def get_teams_by_conference(request: Request, conference: str, db: AsyncSession = Depends(get_db)):
    return await service.get_teams_by_conference(db=db, conference=conference)

@router.get("/{abbrev}/roster/{season}")
async def get_team_roster(request: Request,abbrev, season, db: AsyncSession = Depends(get_db)):
    return await service.get_team_roster_by_id_in_db(db=db, abbrev=abbrev, season=season)

