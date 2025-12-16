#!/usr/bin/env python3
"""
Script to populate the NBA players database.

This script uses the get_team_roster_per_season function from players.py
to fetch all current NBA players and populate the players table.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import time

# Add the Backend/src directory to Python path
backend_src_dir = Path(__file__).parent.parent
if str(backend_src_dir) not in sys.path:
    sys.path.insert(0, str(backend_src_dir))

from db.database import async_session
from db.models import Players
from db.schemas import PlayerCreate
from players import player
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

# All NBA teams
"""
teams_list = [
    'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DET', 'IND',
    'MIA', 'MIL', 'NYK', 'ORL', 'PHI', 'TOR', 'WAS',  # Eastern Conference
    'DAL', 'DEN', 'GSW', 'HOU', 'LAC', 'LAL', 'MEM', 'MIN',
    'NOP', 'OKC', 'PHX', 'POR', 'SAC', 'SAS', 'UTA'   # Western Conference
]
"""

teams_list = ['SAS']


def parse_birth_date(birth_date_str: str) -> datetime:
    """Parse birth date string to datetime object."""
    try:
        # Handle different date formats that might come from the API
        formats = [
            "%B %d, %Y",      # "January 1, 1990"
            "%b %d, %Y",      # "Jan 1, 1990"  
            "%m/%d/%Y",       # "01/01/1990"
            "%Y-%m-%d"        # "1990-01-01"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(birth_date_str, fmt)
            except ValueError:
                continue
                
        # If none of the formats work, raise an error
        raise ValueError(f"Unable to parse date: {birth_date_str}")
        
    except Exception as e:
        print(f"Error parsing birth date '{birth_date_str}': {e}")
        # Return a default date if parsing fails
        return datetime(1990, 1, 1)


def parse_rookie_season(rookie_season_str: str) -> int:
    """Parse rookie season string to integer year."""
    try:
        if isinstance(rookie_season_str, str):
            # Handle formats like "2020-21" -> 2020
            if '-' in rookie_season_str:
                return int(rookie_season_str.split('-')[0])
            # Handle formats like "2020" -> 2020
            return int(rookie_season_str)
        return int(rookie_season_str)
    except (ValueError, AttributeError):
        # Default to current year if parsing fails
        return datetime.now().year


async def populate_players_table():
    """
    Populate the players table with all current NBA players.
    
    Returns:
        Dictionary with operation results
    """
    try:
        player_instance = player()
        players_added = 0
        players_skipped = 0
        errors = 0
        
        async with async_session() as session:
            # Get existing player IDs to avoid duplicates
            existing_players_result = await session.execute(select(Players.player_id))
            existing_player_ids = {row[0] for row in existing_players_result.fetchall()}
            
            print(f"Found {len(existing_player_ids)} existing players in database")
            
            # Process each team
            for team_abbr in teams_list:
                print(f"\n📋 Processing team: {team_abbr}")
                
                try:
                    # Get team roster
                    roster_df = player_instance.get_team_roster_per_season(team_abbr)
                    
                    print(f"   Found {len(roster_df)} players on roster")
                    
                    # Process each player in the roster
                    for player_id, row in roster_df.iterrows():
                        try:
                            # Skip if player already exists
                            if player_id in existing_player_ids:
                                players_skipped += 1
                                continue
                            
                            # Parse birth date
                            birth_date = parse_birth_date(row['BIRTH_DATE'])
                            
                            # Parse rookie season
                            rookie_season = parse_rookie_season(row['ROOKIE_SEASON'])
                            
                            # Create new player record
                            new_player = Players(
                                player_id=player_id,
                                player_name=row['PLAYER'],
                                position=row.get('POSITION'),
                                height=row.get('HEIGHT'),
                                weight=row.get('WEIGHT'),
                                birth_date=birth_date,
                                school=row.get('SCHOOL'),
                                rookie_season=rookie_season
                            )
                            
                            session.add(new_player)
                            existing_player_ids.add(player_id)  # Track to avoid duplicates in same run
                            players_added += 1
                            
                            print(f"   ✅ Added: {row['PLAYER']} (ID: {player_id})")
                            
                        except Exception as e:
                            print(f"   ❌ Error processing player {row.get('PLAYER', 'Unknown')}: {e}")
                            errors += 1
                            continue
                    
                    # Add delay between teams to respect API rate limits
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   ❌ Error processing team {team_abbr}: {e}")
                    errors += 1
                    continue
            
            # Commit all changes
            await session.commit()
            
            print(f"\n🎉 Players population completed:")
            print(f"   • Players added: {players_added}")
            print(f"   • Players skipped (already exist): {players_skipped}")
            print(f"   • Errors encountered: {errors}")
            print(f"   • Total teams processed: {len(teams_list)}")
            
            return {
                "success": True,
                "players_added": players_added,
                "players_skipped": players_skipped,
                "errors": errors,
                "teams_processed": len(teams_list)
            }
            
    except Exception as e:
        print(f"❌ Error populating players table: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_players_from_db():
    """
    Retrieve all players from the database.
    
    Returns:
        List of Players objects from the database
    """
    try:
        async with async_session() as session:
            result = await session.execute(select(Players))
            players = result.scalars().all()
            return players
    except Exception as e:
        print(f"Error retrieving players from database: {e}")
        raise e


async def clear_players_table():
    """
    Clear all players from the database. Use with caution!
    
    Returns:
        Dictionary with operation result
    """
    try:
        async with async_session() as session:
            # Get count before deletion
            count_result = await session.execute(select(Players))
            players_count = len(count_result.scalars().all())
            
            # Delete all players
            await session.execute(Players.__table__.delete())
            await session.commit()
            
            print(f"Cleared {players_count} players from database")
            return {
                "success": True,
                "players_deleted": players_count
            }
            
    except Exception as e:
        print(f"Error clearing players table: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def run_populate_players():
    """
    Synchronous wrapper to run populate_players_table().
    """
    return asyncio.run(populate_players_table())


def run_clear_players():
    """
    Synchronous wrapper to run clear_players_table().
    """
    return asyncio.run(clear_players_table())


async def main():
    """Main function to populate players and display results."""
    
    print("🏀 NBA Players Database Population Tool")
    print("=" * 50)
    
    # Show current players count
    try:
        current_players = await get_players_from_db()
        print(f"\n📊 Current players in database: {len(current_players)}")
    except Exception as e:
        print(f"\n📊 Could not get current player count: {e}")
    
    # Populate players table
    print("\n📥 Fetching players data from NBA API...")
    print("⚠️  This may take several minutes due to API rate limits...")
    
    result = await populate_players_table()
    
    if result["success"]:
        print("\n✅ Players population completed successfully!")
    else:
        print("\n❌ Players population failed!")
        print(f"Error: {result['error']}")
        return
    
    # Display updated count
    try:
        updated_players = await get_players_from_db()
        print(f"\n📊 Total players now in database: {len(updated_players)}")
        
        # Show some sample players
        if updated_players:
            print(f"\n📋 Sample players:")
            for player in updated_players[:5]:
                print(f"   • {player.player_name} (ID: {player.player_id}) - Rookie: {player.rookie_season}")
                
    except Exception as e:
        print(f"Error retrieving updated player count: {e}")


if __name__ == "__main__":
    asyncio.run(main())
