#!/usr/bin/env python3
"""
Quick test for the teams API endpoints.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from handler.teams.service import get_all_teams, get_team_by_abbreviation


async def test_api_functions():
    """Test the service functions directly."""
    
    print("🧪 Testing Teams API Functions")
    print("=" * 40)
    
    # Test get_all_teams
    print("\n1️⃣ Testing get_all_teams()...")
    try:
        teams = get_all_teams()
        print(f"   ✅ Success! Retrieved {len(teams)} teams")
        print(f"   📊 Sample team: {teams[0]['full_name']} ({teams[0]['abbreviation']})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test get_team_by_abbreviation
    print("\n2️⃣ Testing get_team_by_abbreviation('LAL')...")
    try:
        team = get_team_by_abbreviation('LAL')
        print(f"   ✅ Success! Retrieved: {team['full_name']}")
        print(f"   🏀 Conference: {team['conference']}")
        print(f"   🏛️ City: {team['city']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test database teams with logos
    print("\n3️⃣ Testing database teams with logo paths...")
    try:
        from db.static_data import get_teams_from_db
        teams = await get_teams_from_db()
        
        # Show a few teams with their logos
        sample_teams = ['LAL', 'BOS', 'GSW', 'MIA', 'CHI']
        for abbrev in sample_teams:
            team = next((t for t in teams if t.abbreviation == abbrev), None)
            if team:
                logo_status = "✅" if team.logo else "❌"
                print(f"   {logo_status} {team.full_name} ({team.abbreviation})")
                if team.logo:
                    print(f"      Logo: {team.logo}")
        
        teams_with_logos = sum(1 for t in teams if t.logo)
        print(f"\n   📊 Total teams with logos: {teams_with_logos}/30")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🎉 API function tests completed!")


if __name__ == "__main__":
    asyncio.run(test_api_functions())