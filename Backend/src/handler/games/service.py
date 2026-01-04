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

# Import games functions directly
import sys
from pathlib import Path
functions_path = Path(__file__).resolve().parents[2] / "Functions"
if str(functions_path) not in sys.path:
    sys.path.insert(0, str(functions_path))

from games import get_todays_games as get_todays_games_func, get_current_standings, get_todays_games

# ------------------ Games information ------------------ #

async def get_todays_games():
    """
    Retrieve today's games from the API.
    
    Returns:
        List of Games objects from the database
    """
    try:
        todays_games = get_todays_games_func()
        if todays_games is None:
            raise HTTPException(status_code=404, detail="No games found for today")
        return todays_games
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving today's games: {e}")
        raise e
    
async def get_standings(season: str, conference: str = 'Overall'):
    """
    Retrieve standings for a given season and conference from the API.
    
    Returns:
        Standings DataFrame
    """
    try:
        standings_df = get_current_standings(season=season, conference=conference)
        if standings_df is None or standings_df.empty:
            raise HTTPException(status_code=404, detail="No standings found for the given season and conference")
        return standings_df.to_dict(orient='records')
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving standings: {e}")
        raise e
    
async def get_games_of_today():
    try:
        games = get_todays_games_func()
        if games is None:
            raise HTTPException(status_code=404, detail="No games found for today")
        return games
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving today's games: {e}")
        raise HTTPException(status_code=500, detail=str(e))