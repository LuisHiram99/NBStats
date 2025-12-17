#!/usr/bin/env python3
"""
Debug script to check teams and player associations in the database
"""
import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from sqlalchemy import select, func
from db.database import async_session
from db.models import Teams, Players, PlayerTeamsAssociation

async def debug_teams_data():
    async with async_session() as db:
        # Check all teams
        print("=== ALL TEAMS ===")
        teams_result = await db.execute(select(Teams))
        teams = teams_result.scalars().all()
        
        for team in teams:
            print(f"ID: {team.team_id}, Abbrev: {team.abbreviation}, Name: {team.full_name}")
        
        print(f"\nTotal teams: {len(teams)}")
        
        # Check player-team associations
        print("\n=== PLAYER-TEAM ASSOCIATIONS BY SEASON ===")
        associations_result = await db.execute(
            select(
                PlayerTeamsAssociation.team_id,
                PlayerTeamsAssociation.season,
                func.count(PlayerTeamsAssociation.player_id).label('player_count')
            )
            .group_by(PlayerTeamsAssociation.team_id, PlayerTeamsAssociation.season)
            .order_by(PlayerTeamsAssociation.team_id, PlayerTeamsAssociation.season)
        )
        associations = associations_result.all()
        
        for assoc in associations:
            # Get team abbreviation
            team_result = await db.execute(
                select(Teams.abbreviation)
                .where(Teams.team_id == assoc.team_id)
            )
            team_abbrev = team_result.scalar_one_or_none()
            print(f"Team ID: {assoc.team_id} ({team_abbrev}), Season: {assoc.season}, Players: {assoc.player_count}")
        
        # Check available seasons
        print("\n=== ALL SEASONS ===")
        seasons_result = await db.execute(
            select(PlayerTeamsAssociation.season)
            .distinct()
            .order_by(PlayerTeamsAssociation.season)
        )
        seasons = seasons_result.scalars().all()
        for season in seasons:
            print(f"Season: {season}")

if __name__ == "__main__":
    asyncio.run(debug_teams_data())