from fastapi import HTTPException, Request
import sys
from pathlib import Path
import json
from typing import List
from .teams_functions import get_team_roster_per_season
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
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

async def get_all_team_ids(db: AsyncSession):
    """Get all team IDs and names for debugging purposes"""
    try:
        result = await db.execute(
            select(models.Teams.team_id, models.Teams.full_name, models.Teams.abbreviation, models.Teams.logo)
        )
        teams = result.all()
        return [schemas.TeamBasicInfoResponse(
                team_id=team.team_id, 
                full_name=team.full_name, 
                abbreviation=team.abbreviation,
                logo=team.logo) for team in teams]
    except Exception as e:
        print(f"Error retrieving team IDs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
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
        
        if not teams:
            raise HTTPException(status_code=404, detail="No teams found for this conference")
        
        return [schemas.TeamBasicInfoResponse.model_validate(team) for team in teams]
    
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
    
async def get_team_roster_by_id_in_db(db: AsyncSession, season: str, abbrev: str):
    """
    Retrieve the roster for a specific team by its ID for a given season.
    
    Args:
        season (str): The season year (e.g., "2023-24")
        team_id (int): The team's unique identifier
    Returns:
        List of player dictionaries representing the team's roster
    """
    try:
        team_id_query = await db.execute(
            select(models.Teams.team_id)
            .where(models.Teams.abbreviation == abbrev)
        )

        team_id_query = team_id_query.scalar_one_or_none()
        if team_id_query is None:
            raise HTTPException(status_code=404, detail="Team not found")
        players = await db.execute(
            select(models.Players)
            .join(models.PlayerTeamsAssociation, models.Players.player_id == models.PlayerTeamsAssociation.player_id)
            .where(models.PlayerTeamsAssociation.team_id == team_id_query)
            .where(models.PlayerTeamsAssociation.season == season)
        ) 
        
        players = players.scalars().all()
        if not players:
            raise HTTPException(status_code=404, detail="No players found for this team in the specified season")
        return players
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving roster for team ID {team_id_query} in season {season}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ------------------ User Favorite Teams Management ------------------ #
async def add_favorite_team_for_user(db: AsyncSession, user_id: int, teams_id_list: List[int]) -> dict:
    """
    Add favorite teams for a user.
    
    Args:
        db (AsyncSession): Database session
        user_id (int): The user's unique identifier
        teams_id_list (List[int]): List of team IDs to add as favorites
    Returns:
        dict: Success message with details
    """
    
    try:
        # First check if user exists
        user_check = await db.execute(
            select(models.Users).where(models.Users.id == user_id)
        )
        if not user_check.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        for team_id in teams_id_list:
            
            # Check if association already exists
            existing = await db.execute(
                select(models.UsersTeamsAssociation)
                .where(models.UsersTeamsAssociation.user_id == user_id)
                .where(models.UsersTeamsAssociation.team_id == team_id)
            )
            if existing.scalar_one_or_none():
                continue
                
            # Check if team exists
            db_team = await db.execute(
                select(models.Teams)
                .where(models.Teams.team_id == team_id)
            )
            team = db_team.scalar_one_or_none()
            if team is None:
                raise HTTPException(status_code=404, detail=f"Team with ID {team_id} not found")
                
            # Add to favorites
            association = models.UsersTeamsAssociation(
                user_id=user_id,
                team_id=team_id
            )
            db.add(association)
        await db.commit()
        
        return {
            "message": "Team(s) added successfully to favorites"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding favorite teams for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_favorite_teams_for_user(db: AsyncSession, user_id: int) -> List[schemas.TeamResponse]:
    """
    Retrieve favorite teams for a user.
    
    Args:
        db (AsyncSession): Database session
        user_id (int): The user's unique identifier
    Returns:
        List of TeamResponse objects representing the user's favorite teams
    """
    
    try:
        # First check if user exists
        user_check = await db.execute(
            select(models.Users).where(models.Users.id == user_id)
        )
        user = user_check.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        
        # Get user's favorite teams
        db_teams = await db.execute(
            select(models.Teams)
            .join(models.UsersTeamsAssociation, models.Teams.team_id == models.UsersTeamsAssociation.team_id)
            .where(models.UsersTeamsAssociation.user_id == user_id)
        )
        teams = db_teams.scalars().all()
        
        # Convert to response format
        if not teams:
            return []  # Return empty list if no favorites
        
        result = [schemas.TeamResponse.model_validate(team) for team in teams]
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def remove_favorite_team_for_user(db: AsyncSession, user_id: int, teams_id_list: List[int]) -> dict:
    """
    Remove favorite teams for a user.
    
    Args:
        db (AsyncSession): Database session
        user_id (int): The user's unique identifier
        teams_id_list (List[int]): List of team IDs to remove from favorites
    Returns:
        dict: Success message with details
    """
    try:
        # First check if user exists
        user_check = await db.execute(
            select(models.Users).where(models.Users.id == user_id)
        )
        user = user_check.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        for team in teams_id_list:
            # Check if association already exists
            existing = await db.execute(
                select(models.UsersTeamsAssociation)
                .where(models.UsersTeamsAssociation.user_id == user_id)
                .where(models.UsersTeamsAssociation.team_id == team)
            )
            db_existing = existing.scalar_one_or_none()

            if not db_existing:
                raise HTTPException(status_code=404, detail=f"Team with ID {team} is not in user's favorites")
            await db.delete(db_existing)
        await db.commit()
        return {
            "message": "Favorite teams removed successfully",
            "removed_teams": teams_id_list
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))