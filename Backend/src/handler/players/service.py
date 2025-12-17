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


# ------------------ Players Overall information ------------------ #
async def get_players_from_db(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Retrieve all players from the database, with pagination.
    
    Returns:
        List of Players objects from the database
    """
    try:
        db_players = await db.execute(
            select(models.Players).offset(skip).limit(limit)
        )
        players = db_players.scalars().all()
        if players is None:
            raise HTTPException(status_code=404, detail="No players found in the database")
        return players
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving players from database: {e}")
        raise e
    
async def get_player_by_id(db: AsyncSession, player_id: int):
    try:
        db_player = await db.execute(
            select(models.Players)
            .where(models.Players.player_id == player_id)
        )

        player = db_player.scalar_one_or_none()
        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")
        return schemas.PlayerResponse.model_validate(player)
    except HTTPException:
        raise 
    except Exception as e:
        print(f"Error getting player by ID: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_player_by_name(db: AsyncSession, name: str):
    try:
        db_player = await db.execute(
            select(models.Players)
            .where(models.Players.player_name.ilike(f"%{name}%"))
        )

        player = db_player.scalars().all()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        return player
    except HTTPException:
        raise 
    except Exception as e:
        print(f"Error getting player by name: {e}")
        raise HTTPException(status_code=500, detail=str(e))