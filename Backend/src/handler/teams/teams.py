from typing import List, Annotated
from fastapi import APIRouter, Depends, Request
from auth.auth import get_current_user
from . import service
from db.schemas import TeamResponse, FavoriteTeamsRequest, TeamBasicInfoResponse
from ..rate_limiter import limiter
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

user_dependency = Annotated[dict, Depends(get_current_user)]



router = APIRouter(
    prefix="/teams",
    tags=["teams"]
)


@router.get("/all", response_model=List[TeamResponse])
@limiter.limit("10/minute")
async def get_all_teams(
    request: Request, 
    db: AsyncSession = Depends(get_db)):
    """
        Get all available teams
    """
    teams = await service.get_teams_from_db(db=db)
    return [TeamResponse.model_validate(team) for team in teams]

@router.get("/ids", response_model=List[TeamBasicInfoResponse])
@limiter.limit("10/minute") 
async def get_all_team_ids(
    request: Request, 
    db: AsyncSession = Depends(get_db)):
    """Get all available team IDs and names for debugging"""
    teams = await service.get_all_team_ids(db=db) 
    return [TeamBasicInfoResponse.model_validate(team) for team in teams]

# User's favorite teams endpoints 
@router.get("/favorites", response_model=List[TeamResponse])
@limiter.limit("10/minute")
async def get_favorite_teams(
    request: Request, 
    current_user: user_dependency, 
    db: AsyncSession = Depends(get_db)):
    return await service.get_favorite_teams_for_user(db=db, user_id=current_user["user_id"])

@router.post("/favorites")
@limiter.limit("5/minute")
async def add_favorite_team(
    request: Request, 
    favorite_teams: FavoriteTeamsRequest,
    current_user: user_dependency, 
    db: AsyncSession = Depends(get_db)
) -> dict:
    return await service.add_favorite_team_for_user(
        db=db, 
        user_id=current_user["user_id"], 
        teams_id_list=favorite_teams.team_ids
    )

@router.delete("/favorites")
@limiter.limit("5/minute")
async def remove_favorite_team(
    request: Request, 
    favorite_teams: FavoriteTeamsRequest,
    current_user: user_dependency, 
    db: AsyncSession = Depends(get_db)
) -> dict:
    return await service.remove_favorite_team_for_user(
        db=db, 
        user_id=current_user["user_id"], 
        teams_id_list=favorite_teams.team_ids
    )

@router.get("/ids/{team_id}", response_model=TeamResponse)
@limiter.limit("10/minute")
async def get_team_by_id(request: Request, team_id:int, db: AsyncSession = Depends(get_db)):
    return await service.get_single_team_by_id(db=db, team_id=team_id)

@router.get("/conference/{conference}", response_model=List[TeamBasicInfoResponse])
@limiter.limit("10/minute")
async def get_teams_by_conference(request: Request, conference: str, db: AsyncSession = Depends(get_db)):
    return await service.get_teams_by_conference(db=db, conference=conference)

@router.get("/{abbrev}", response_model=TeamResponse)
@limiter.limit("10/minute")
async def get_team_by_abbreviation(request: Request, abbrev: str, db: AsyncSession = Depends(get_db)):
    return await service.get_team_by_abbreviation(db=db, abbrev=abbrev)

@router.get("/{abbrev}/roster/{season}")
@limiter.limit("10/minute")
async def get_team_roster(request: Request,abbrev, season, db: AsyncSession = Depends(get_db)):
    return await service.get_team_roster_by_id_in_db(db=db, abbrev=abbrev, season=season)