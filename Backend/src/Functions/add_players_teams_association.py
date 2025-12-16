#!/usr/bin/env python3
"""
Script to populate the player-team associations table.

This script uses the get_player_teams function from players.py
to fetch all player-team associations and populate the player_teams_association table.
"""

import asyncio
import sys
from pathlib import Path
import time

# Add the Backend/src directory to Python path
backend_src_dir = Path(__file__).parent.parent
if str(backend_src_dir) not in sys.path:
    sys.path.insert(0, str(backend_src_dir))

from db.database import async_session
from db.models import Players, Teams, PlayerTeamsAssociation
from db.schemas import PlayerTeamAssociationCreate
from players import player
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


async def populate_player_teams_associations():
    """
    Populate the player_teams_association table with all player-team relationships.
    
    Returns:
        Dictionary with operation results
    """
    try:
        player_instance = player()
        associations_added = 0
        associations_skipped = 0
        errors = 0
        
        async with async_session() as session:
            # Get all players from database
            players_result = await session.execute(select(Players))
            all_players = players_result.scalars().all()
            
            print(f"📋 Found {len(all_players)} players in database")
            
            # Get existing associations to avoid duplicates
            existing_associations_result = await session.execute(
                select(PlayerTeamsAssociation.player_id, 
                       PlayerTeamsAssociation.team_id, 
                       PlayerTeamsAssociation.season)
            )
            existing_associations = {
                (row[0], row[1], row[2]) for row in existing_associations_result.fetchall()
            }
            
            print(f"📊 Found {len(existing_associations)} existing associations")
            
            # Process each player
            for idx, player_obj in enumerate(all_players, 1):
                try:
                    print(f"\n👤 [{idx}/{len(all_players)}] Processing: {player_obj.player_name} (ID: {player_obj.player_id})")
                    
                    # Get player's team history
                    player_teams_df = player_instance.get_player_teams(player_obj.player_id)
                    
                    if player_teams_df.empty:
                        print(f"   ⚠️  No team history found for {player_obj.player_name}")
                        continue
                    
                    print(f"   📅 Found {len(player_teams_df)} season(s)")
                    
                    # Process each team association
                    for _, row in player_teams_df.iterrows():
                        try:
                            player_id = int(row['PLAYER_ID'])
                            team_id = int(row['TEAM_ID'])
                            season = str(row['SEASON_ID'])
                            
                            # Skip invalid team IDs (NBA API sometimes returns 0 for special cases)
                            if team_id == 0:
                                print(f"   ⚠️  Skipped invalid team ID: {season} - Team ID {team_id}")
                                continue
                            
                            # Check if association already exists
                            if (player_id, team_id, season) in existing_associations:
                                associations_skipped += 1
                                continue
                            
                            # Create new association record
                            new_association = PlayerTeamsAssociation(
                                player_id=player_id,
                                team_id=team_id,
                                season=season
                            )
                            
                            session.add(new_association)
                            existing_associations.add((player_id, team_id, season))  # Track to avoid duplicates in same run
                            associations_added += 1
                            
                            print(f"   ✅ Added: {season} - Team ID {team_id}")
                            
                        except Exception as e:
                            print(f"   ❌ Error processing association for season {row.get('SEASON_ID', 'Unknown')}: {e}")
                            errors += 1
                            continue
                    
                    # Add delay between players to respect API rate limits
                    time.sleep(0.8)
                    
                    # Commit in batches to avoid memory issues
                    if idx % 50 == 0:
                        await session.commit()
                        print(f"\n💾 Batch commit completed for {idx} players")
                    
                except Exception as e:
                    print(f"   ❌ Error processing player {player_obj.player_name}: {e}")
                    errors += 1
                    continue
            
            # Final commit
            await session.commit()
            
            print(f"\n🎉 Player-Team associations population completed:")
            print(f"   • Associations added: {associations_added}")
            print(f"   • Associations skipped (already exist): {associations_skipped}")
            print(f"   • Errors encountered: {errors}")
            print(f"   • Players processed: {len(all_players)}")
            
            return {
                "success": True,
                "associations_added": associations_added,
                "associations_skipped": associations_skipped,
                "errors": errors,
                "players_processed": len(all_players)
            }
            
    except Exception as e:
        print(f"❌ Error populating associations table: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_associations_from_db():
    """
    Retrieve all player-team associations from the database.
    
    Returns:
        List of PlayerTeamsAssociation objects from the database
    """
    try:
        async with async_session() as session:
            result = await session.execute(select(PlayerTeamsAssociation))
            associations = result.scalars().all()
            return associations
    except Exception as e:
        print(f"Error retrieving associations from database: {e}")
        raise e


async def clear_associations_table():
    """
    Clear all associations from the database. Use with caution!
    
    Returns:
        Dictionary with operation result
    """
    try:
        async with async_session() as session:
            # Get count before deletion
            count_result = await session.execute(select(PlayerTeamsAssociation))
            associations_count = len(count_result.scalars().all())
            
            # Delete all associations
            await session.execute(PlayerTeamsAssociation.__table__.delete())
            await session.commit()
            
            print(f"Cleared {associations_count} associations from database")
            return {
                "success": True,
                "associations_deleted": associations_count
            }
            
    except Exception as e:
        print(f"Error clearing associations table: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_associations_stats():
    """
    Get statistics about the associations table.
    
    Returns:
        Dictionary with statistics
    """
    try:
        async with async_session() as session:
            # Get total associations
            total_result = await session.execute(select(PlayerTeamsAssociation))
            total_associations = len(total_result.scalars().all())
            
            # Get unique players count
            unique_players_result = await session.execute(
                select(PlayerTeamsAssociation.player_id).distinct()
            )
            unique_players = len(unique_players_result.fetchall())
            
            # Get unique teams count
            unique_teams_result = await session.execute(
                select(PlayerTeamsAssociation.team_id).distinct()
            )
            unique_teams = len(unique_teams_result.fetchall())
            
            # Get unique seasons count
            unique_seasons_result = await session.execute(
                select(PlayerTeamsAssociation.season).distinct()
            )
            unique_seasons = len(unique_seasons_result.fetchall())
            
            return {
                "total_associations": total_associations,
                "unique_players": unique_players,
                "unique_teams": unique_teams,
                "unique_seasons": unique_seasons
            }
            
    except Exception as e:
        print(f"Error getting associations statistics: {e}")
        return {}


def run_populate_associations():
    """
    Synchronous wrapper to run populate_player_teams_associations().
    """
    return asyncio.run(populate_player_teams_associations())


def run_clear_associations():
    """
    Synchronous wrapper to run clear_associations_table().
    """
    return asyncio.run(clear_associations_table())


async def main():
    """Main function to populate associations and display results."""
    
    print("🏀 NBA Player-Team Associations Population Tool")
    print("=" * 55)
    
    # Show current statistics
    try:
        current_stats = await get_associations_stats()
        print(f"\n📊 Current database statistics:")
        print(f"   • Total associations: {current_stats.get('total_associations', 0)}")
        print(f"   • Unique players: {current_stats.get('unique_players', 0)}")
        print(f"   • Unique teams: {current_stats.get('unique_teams', 0)}")
        print(f"   • Unique seasons: {current_stats.get('unique_seasons', 0)}")
    except Exception as e:
        print(f"\n📊 Could not get current statistics: {e}")
    
    # Populate associations table
    print("\n📥 Fetching player-team associations from NBA API...")
    print("⚠️  This will take a significant amount of time due to API rate limits...")
    print("    (Approximately 1 second per player + processing time)")
    
    result = await populate_player_teams_associations()
    
    if result["success"]:
        print("\n✅ Associations population completed successfully!")
    else:
        print("\n❌ Associations population failed!")
        print(f"Error: {result['error']}")
        return
    
    # Display updated statistics
    try:
        updated_stats = await get_associations_stats()
        print(f"\n📊 Updated database statistics:")
        print(f"   • Total associations: {updated_stats.get('total_associations', 0)}")
        print(f"   • Unique players: {updated_stats.get('unique_players', 0)}")
        print(f"   • Unique teams: {updated_stats.get('unique_teams', 0)}")
        print(f"   • Unique seasons: {updated_stats.get('unique_seasons', 0)}")
        
        # Show some sample associations
        try:
            sample_associations = await get_associations_from_db()
            if sample_associations:
                print(f"\n📋 Sample associations:")
                for assoc in sample_associations[:5]:
                    print(f"   • Player {assoc.player_id} - Team {assoc.team_id} - Season {assoc.season}")
        except Exception as e:
            print(f"Could not retrieve sample associations: {e}")
                
    except Exception as e:
        print(f"Error retrieving updated statistics: {e}")


if __name__ == "__main__":
    asyncio.run(main())
