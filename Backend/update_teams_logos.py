#!/usr/bin/env python3
"""
Script to update teams in the database with logo paths.
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

from db.static_data import update_teams_data, get_teams_from_db


async def main():
    """Main function to update teams with logo paths."""
    
    print("🏀 NBA Teams Logo Update Tool")
    print("=" * 40)
    
    # Update teams with logo paths
    print("\n📝 Updating teams data with logo paths...")
    result = await update_teams_data()
    
    if result["success"]:
        print("✅ Teams update completed successfully!")
        print(f"   • Teams updated: {result['teams_updated']}")
    else:
        print("❌ Teams update failed!")
        print(f"   • Error: {result['error']}")
        return
    
    # Display sample teams with logo paths
    print("\n🖼️ Sample teams with logo paths:")
    try:
        teams = await get_teams_from_db()
        
        # Show first 5 teams with their logo paths
        for i, team in enumerate(teams[:5]):
            logo_status = "✅" if team.logo else "❌"
            print(f"   {logo_status} {team.full_name} ({team.abbreviation})")
            if team.logo:
                print(f"      Logo: {team.logo}")
            else:
                print(f"      Logo: No logo path found")
                
        # Count teams with and without logos
        with_logos = sum(1 for t in teams if t.logo)
        without_logos = len(teams) - with_logos
        
        print(f"\n📊 Logo Statistics:")
        print(f"   • Teams with logos: {with_logos}")
        print(f"   • Teams without logos: {without_logos}")
                
    except Exception as e:
        print(f"   • Error retrieving teams: {e}")


if __name__ == "__main__":
    asyncio.run(main())