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
from db.database import async_session
from db.models import Teams
from db import models, schemas

# ------------------ Teams Overall information ------------------ #

async def get_teams_from_db(db: AsyncSession):
    """
    Retrieve all teams from the database.
    
    Returns:
        List of Teams objects from the database
    """
    try:
        db_teams = await db.execute(
            select(models.Teams)
        )
        teams = db_teams.scalars().all()
        if teams is None:
            raise HTTPException(status_code=404, detail="No teams found in the database")
        return teams
    except HTTPException:
        raise
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
async def get_team_roster_by_abbrev(db: AsyncSession,season: str, abbrev: str):
    """
    Retrieve the roster for a specific team by its abbreviation for a given season.
    
    Args:
        season (str): The season year (e.g., "2023-24")
        abbrev (str): The team's abbreviation (e.g., "LAL" for Los Angeles Lakers)
        
    Returns:
        List of player dictionaries representing the team's roster
    """
    try:
        import sys
        from pathlib import Path
        
        # Add the Backend/src/Functions path
        src_functions_path = Path(__file__).resolve().parents[2] / "Functions"
        if str(src_functions_path) not in sys.path:
            sys.path.insert(0, str(src_functions_path))
            
        from teams import get_team_roster_per_season
        
        team_id_query = await db.execute(
            select(models.Teams.team_id)
            .where(models.Teams.abbreviation == abbrev)
        )

        team_id_result = team_id_query.scalar_one_or_none()
        if team_id_result is None:
            raise HTTPException(status_code=404, detail="Team not found")
    
        roster_json = get_team_roster_per_season(season=season, team_id=team_id_result)
        roster = json.loads(roster_json)
        return roster
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving roster for team {abbrev} in season {season}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
