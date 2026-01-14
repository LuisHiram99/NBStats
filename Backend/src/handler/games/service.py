from fastapi import HTTPException
import json 
from datetime import datetime
import redis
from .games_functions import get_current_season, get_current_standings, get_todays_games_function

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
CACHE_TTL = 60 * 10

# ------------------ Games information ------------------ #

async def get_standings(season: str, conference: str = 'Overall'):
    """
    Retrieve standings for a given season and conference from the API.

    Args:
        season (str): Season in 'YYYY-YY' format
        conference (str): 'Overall', 'East', or 'West'
    
    Returns:
        Standings DataFrame
    """

    # Get current season for caching purposes
    current_season = get_current_season()
    # Create cache key
    cache_key = f"standings:{current_season}:{conference}"
    try:
        # Check Redis cache first
        cached_data = redis_client.get(cache_key)
        if cached_data:
            # If cached, return the cached standings
            return json.loads(cached_data)
        # If not cached, fetch from the API
        standings_df = get_current_standings(season=season, conference=conference)
        # Check if standings_df is valid
        if standings_df is None or standings_df.empty:
            raise HTTPException(status_code=404, detail="No standings found for the given season and conference")
        
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
    # Create cache key
    today = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"todays_games:{today}" 

    try:
        # Check Redis cache first
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        # If not cached, fetch games from the API
        todays_games = get_todays_games_function()
        if todays_games is None:
            raise HTTPException(status_code=404, detail="No games found for today")
        
        # Cache the result games in Redis
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
    
    