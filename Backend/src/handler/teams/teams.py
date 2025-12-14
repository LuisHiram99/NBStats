from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from . import service
from db.static_data import populate_teams_table, clear_teams_table, update_teams_data, get_teams_from_db
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
async def get_all_teams(request: Request):
    teams = await service.get_teams_from_db()
    return [TeamResponse.model_validate(team) for team in teams]


@router.get("/{abbrev}")
async def get_team_by_abbreviation(request: Request, abbrev: str, db: AsyncSession = Depends(get_db)):
    return await service.get_team_by_abbreviation(db=db, abbrev=abbrev)

@router.get("/conference/{conference}")
async def get_teams_by_conference(request: Request, conference: str, db: AsyncSession = Depends(get_db)):
    return await service.get_teams_by_conference(db=db, conference=conference)

@router.get("/{abbrev}/roster/{season}")
async def get_team_roster(abbrev, season):
    return await service.get_team_roster_by_abbrev(abbrev=abbrev, season=season)
