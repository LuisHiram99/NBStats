#!/usr/bin/env python3
"""
Script to populate the NBA teams database.

This script uses the static_data module to populate the teams table
with data fetched from the NBA API using the get_all_teams() function.

Usage:
    python populate_teams.py
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Also add the Datos/Functions directory to handle imports
datos_path = current_dir.parent / "Datos" / "Functions"
if str(datos_path) not in sys.path:
    sys.path.insert(0, str(datos_path))

from db.static_data import populate_teams_table, get_teams_from_db


async def main():
    """Main function to populate teams and display results."""
    
    print("🏀 NBA Teams Database Population Tool")
    print("=" * 50)
    
    # Populate teams table
    print("\n📥 Fetching teams data from NBA API...")
    result = await populate_teams_table()
    
    if result["success"]:
        print("✅ Teams population completed successfully!")
        print(f"   • Teams added: {result['teams_added']}")
        print(f"   • Teams skipped (already exist): {result['teams_skipped']}")
        print(f"   • Total teams processed: {result['total_teams']}")
    else:
        print("❌ Teams population failed!")
        print(f"   • Error: {result['error']}")
        return
    
    # Display current teams in database
    print("\n📊 Current teams in database:")
    try:
        teams = await get_teams_from_db()
        print(f"   • Total teams in database: {len(teams)}")
        
        # Group teams by conference
        east_teams = [t for t in teams if t.conference == "East"]
        west_teams = [t for t in teams if t.conference == "West"]
        
        print(f"   • Eastern Conference: {len(east_teams)} teams")
        print(f"   • Western Conference: {len(west_teams)} teams")
        
        # Show some example teams
        if teams:
            print("\n   Sample teams:")
            for team in teams[:5]:
                print(f"     - {team.full_name} ({team.abbreviation}) - {team.conference}")
                
    except Exception as e:
        print(f"   • Error retrieving teams: {e}")


if __name__ == "__main__":
    asyncio.run(main())