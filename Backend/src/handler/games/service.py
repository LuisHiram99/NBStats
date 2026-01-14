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
from datetime import datetime
import redis

# Import games functions directly
import sys
from pathlib import Path
functions_path = Path(__file__).resolve().parents[2] / "Functions"
if str(functions_path) not in sys.path:
    sys.path.insert(0, str(functions_path))

from games import get_todays_games_function, get_current_standings
from helpfuncs import get_current_season

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
CACHE_TTL = 60 * 10

# ------------------ Games information ------------------ #

async def get_standings(season: str, conference: str = 'Overall'):
    """
    Retrieve standings for a given season and conference from the API.
    
    Returns:
        Standings DataFrame
    """
    current_season = get_current_season()
    today = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"standings:{current_season}:{conference}"
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            print("Standings fetched from cache")
            return json.loads(cached_data)
        
        standings_df = get_current_standings(season=season, conference=conference)
        if standings_df is None or standings_df.empty:
            raise HTTPException(status_code=404, detail="No standings found for the given season and conference")
        print("Standings fetched from API")
        # We only cache the current season standings since past seasons don't change
        if season == current_season:
            redis_client.set(cache_key, standings_df.to_json(orient='records'), ex=CACHE_TTL)
        return standings_df.to_dict(orient='records')
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving standings: {e}")
        raise e


async def get_todays_games_service():
    """
    Retrieve today's games from the API.
    
    Returns:
        List of Games objects from the database
    """
    today = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"todays_games:{today}" 

    try:
        # Check Redis cache first
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        # If not cached, fetch from the API
        todays_games = get_todays_games_function()
        if todays_games is None:
            raise HTTPException(status_code=404, detail="No games found for today")
        
        # Cache the result in Redis
        redis_client.set(cache_key, json.dumps(todays_games), ex=CACHE_TTL)

        return todays_games
    except redis.RedisError as re:
        print(f"Redis error: {re}")
        # Proceed without caching if Redis fails
        todays_games = get_todays_games_function()
        return todays_games
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving today's games: {e}")
        raise e
    

async def get_cache_info():
    """
    Retrieve Redis cache information.
    
    Returns:
        Redis info dictionary
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        cache_key = f"todays_games:{today}"

        # Check if key exists and get TTL
        exists = redis_client.exists(cache_key)
        ttl = redis_client.ttl(cache_key)
        info = redis_client.info()
        return {
            "cache_key": cache_key,
            "cache_exists": bool(exists),
            "ttl_seconds": ttl if ttl > 0 else 0,
            "ttl_minutes": round(ttl / 60, 2) if ttl > 0 else 0,
            "redis_info": info
        }
    except redis.RedisError as re:
        print(f"Redis error: {re}")
        raise HTTPException(status_code=500, detail="Redis error")
    except Exception as e:
        print(f"Error retrieving cache info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving cache info")

    