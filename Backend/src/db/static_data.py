import json
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .database import async_session
from .models import Teams
import sys
import os
from pathlib import Path

# Add the Datos/Functions directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent
datos_path = project_root / "Datos" / "Functions"
if str(datos_path) not in sys.path:
    sys.path.insert(0, str(datos_path))

# Import with proper error handling
try:
    from teams import get_all_teams, get_team_details_by_abbreviation
except ImportError as e:
    print(f"Error importing teams module: {e}")
    print(f"Datos path: {datos_path}")
    print(f"Path exists: {datos_path.exists()}")
    raise


async def populate_teams_table():
    """
    Populate the teams table with all NBA teams data from the NBA API.
    
    This function fetches all teams data using the get_all_teams() function
    and inserts them into the database if they don't already exist.
    """
    try:
        # Get all teams data from NBA API
        teams_json = get_all_teams()
        teams_data = json.loads(teams_json)
        
        async with async_session() as session:
            # Check existing teams to avoid duplicates
            existing_teams_result = await session.execute(select(Teams.team_id))
            existing_team_ids = {row[0] for row in existing_teams_result.fetchall()}
            
            teams_added = 0
            teams_skipped = 0
            
            for team_data in teams_data:
                team_id = team_data['id']
                
                # Skip if team already exists
                if team_id in existing_team_ids:
                    teams_skipped += 1
                    continue
                
                # Get additional team details including conference
                team_details = get_team_details_by_abbreviation(team_data['abbreviation'])
                
                # Create new team record
                new_team = Teams(
                    team_id=team_id,
                    full_name=team_data['full_name'],
                    abbreviation=team_data['abbreviation'],
                    nickname=team_data['nickname'],
                    city=team_data['city'],
                    state=team_data['state'],
                    conference=team_details['conference'],
                    year_founded=team_data['year_founded']
                )
                
                session.add(new_team)
                teams_added += 1
            
            # Commit all changes
            await session.commit()
            
            print(f"Teams population completed:")
            print(f"- Teams added: {teams_added}")
            print(f"- Teams skipped (already exist): {teams_skipped}")
            print(f"- Total teams in API: {len(teams_data)}")
            
            return {
                "success": True,
                "teams_added": teams_added,
                "teams_skipped": teams_skipped,
                "total_teams": len(teams_data)
            }
            
    except Exception as e:
        print(f"Error populating teams table: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_teams_from_db():
    """
    Retrieve all teams from the database.
    
    Returns:
        List of Teams objects from the database
    """
    try:
        async with async_session() as session:
            result = await session.execute(select(Teams))
            teams = result.scalars().all()
            return teams
    except Exception as e:
        print(f"Error retrieving teams from database: {e}")
        raise e


async def clear_teams_table():
    """
    Clear all teams from the database. Use with caution!
    
    Returns:
        Dictionary with operation result
    """
    try:
        async with async_session() as session:
            # Get count before deletion
            count_result = await session.execute(select(Teams))
            teams_count = len(count_result.scalars().all())
            
            # Delete all teams
            await session.execute(Teams.__table__.delete())
            await session.commit()
            
            print(f"Cleared {teams_count} teams from database")
            return {
                "success": True,
                "teams_deleted": teams_count
            }
            
    except Exception as e:
        print(f"Error clearing teams table: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def update_teams_data():
    """
    Update existing teams data with fresh data from the NBA API.
    This will update all fields for all teams.
    
    Returns:
        Dictionary with operation result
    """
    try:
        # Get fresh teams data from NBA API
        teams_json = get_all_teams()
        teams_data = json.loads(teams_json)
        
        async with async_session() as session:
            updated_count = 0
            
            for team_data in teams_data:
                team_id = team_data['id']
                
                # Find existing team
                result = await session.execute(select(Teams).where(Teams.team_id == team_id))
                existing_team = result.scalar_one_or_none()
                
                if existing_team:
                    # Get additional team details including conference
                    team_details = get_team_details_by_abbreviation(team_data['abbreviation'])
                    
                    # Update team data
                    existing_team.full_name = team_data['full_name']
                    existing_team.abbreviation = team_data['abbreviation']
                    existing_team.nickname = team_data['nickname']
                    existing_team.city = team_data['city']
                    existing_team.state = team_data['state']
                    existing_team.conference = team_details['conference']
                    existing_team.year_founded = team_data['year_founded']
                    
                    updated_count += 1
            
            await session.commit()
            
            print(f"Updated {updated_count} teams in database")
            return {
                "success": True,
                "teams_updated": updated_count
            }
            
    except Exception as e:
        print(f"Error updating teams data: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def run_populate_teams():
    """
    Synchronous wrapper to run populate_teams_table().
    Use this function if you want to run the population from a regular Python script.
    """
    return asyncio.run(populate_teams_table())


def run_clear_teams():
    """
    Synchronous wrapper to run clear_teams_table().
    Use this function if you want to clear teams from a regular Python script.
    """
    return asyncio.run(clear_teams_table())


def run_update_teams():
    """
    Synchronous wrapper to run update_teams_data().
    Use this function if you want to update teams from a regular Python script.
    """
    return asyncio.run(update_teams_data())


if __name__ == "__main__":
    """
    If this script is run directly, it will populate the teams table.
    """
    print("Starting teams database population...")
    result = run_populate_teams()
    
    if result["success"]:
        print("✅ Teams population completed successfully!")
    else:
        print("❌ Teams population failed!")
        print(f"Error: {result['error']}")
