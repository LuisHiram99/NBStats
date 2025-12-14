from fastapi import HTTPException, Request
import sys
from pathlib import Path
import json

# Add NBStats root to path
nbstats_root = Path(__file__).resolve().parents[4]
datos_path = nbstats_root / "Datos" / "Functions"
if str(datos_path) not in sys.path:
    sys.path.insert(0, str(datos_path))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Teams
from db import models, schemas

# ------------------ Teams Overall information ------------------ #

async def get_teams_from_db():
    """
    Retrieve all teams from the database.
    
    Returns:
        List of Teams objects from the database
    """
    try:
        async with AsyncSession() as session:
            result = await session.execute(select(Teams))
            teams = result.scalars().all()
            return teams
    except Exception as e:
        print(f"Error retrieving teams from database: {e}")
        raise e
    
async def get_team_by_abbreviation(db: AsyncSession, abbrev: str):
    try:
        db_team = await db.execute(
            select(models.Teams)
            .where(models.Teams.abbreviation == abbrev)
        )

        team = db_team.scalar_one_or_none()
        if team is None:
            raise HTTPException(status_code=404, detail="Team not found")
        return schemas.TeamResponse.model_validate(team)
    except HTTPException:
        raise 
    except Exception as e:
        print(f"Error getting team by abbreviation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_teams_by_conference(db: AsyncSession, conference: str):
    try:
        db_teams = await db.execute(
            select(models.Teams)
            .where(models.Teams.conference == conference)
        )

        teams = db_teams.scalars().all()
        return [schemas.TeamResponse.model_validate(team) for team in teams]
        if teams is None:
            raise HTTPException(status_code=404, detail="No teams found for this conference")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting teams by conference: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# ------------------ Teams Roster Information ------------------ #
async def get_team_roster_by_abbrev(season, abbrev):
    try:
        # Get team details first to get the team ID
        team_details = get_team_details_by_abbreviation(team_abbreviation=abbrev)
        team_data = get_team_roster_per_season(team_id=team_details['id'], season=season)
        return team_data.to_json(orient='records')
    except Exception as e:
        print(f"Error getting teams information: {e}")
        raise HTTPException(status_code=500, detail=str(e))
