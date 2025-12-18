#!/usr/bin/env python3
"""
Script to populate RegularSeasonStats table with player statistics.
Uses PlayerTeamsAssociation table to get player-team-season combinations
and fetches stats from NBA API.
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.database import async_session
from db.models import Players, Teams, PlayerTeamsAssociation, RegularSeasonStats

# NBA API imports
from nba_api.stats.endpoints import playercareerstats, playerprofilev2
import pandas as pd
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RegularSeasonStatsPopulator:
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        self.skipped_count = 0
        
    async def get_player_teams_associations(self, session: AsyncSession) -> List[Dict]:
        """Get all player-team associations that need stats populated."""
        try:
            # First, get all players_teams_ids that already have stats
            existing_stats_query = select(RegularSeasonStats.players_teams_id)
            existing_result = await session.execute(existing_stats_query)
            existing_stats_ids = set(row[0] for row in existing_result.all())
            
            # Get current season to exclude it (stats might not be complete)
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            # NBA season typically starts in October
            if current_month >= 10:
                current_season = f"{current_year}-{str(current_year + 1)[-2:]}"
            else:
                current_season = f"{current_year - 1}-{str(current_year)[-2:]}"
            
            logger.info(f"Excluding current season: {current_season}")
            
            # Get all associations with player and team info, excluding current season
            query = select(
                PlayerTeamsAssociation.players_teams_id,
                PlayerTeamsAssociation.player_id,
                PlayerTeamsAssociation.team_id,
                PlayerTeamsAssociation.season,
                Players.player_name,
                Teams.abbreviation.label('team_abbreviation')
            ).join(
                Players, PlayerTeamsAssociation.player_id == Players.player_id
            ).join(
                Teams, PlayerTeamsAssociation.team_id == Teams.team_id
            ).where(
                PlayerTeamsAssociation.season != current_season
            )
            
            result = await session.execute(query)
            associations = []
            
            for row in result.all():
                # Only include associations that don't have stats yet
                if row.players_teams_id not in existing_stats_ids:
                    associations.append({
                        'players_teams_id': row.players_teams_id,
                        'player_id': row.player_id,
                        'team_id': row.team_id,
                        'season': row.season,
                        'player_name': row.player_name,
                        'team_abbreviation': row.team_abbreviation
                    })
                
            logger.info(f"Found {len(associations)} player-team associations needing stats")
            return associations
            
        except Exception as e:
            logger.error(f"Error getting player-team associations: {e}")
            return []

    def get_player_season_stats(self, player_id: int, season: str, max_retries: int = 3) -> Optional[Dict]:
        """Fetch player stats for a specific season from NBA API with retry logic."""
        for attempt in range(max_retries):
            try:
                # More conservative rate limiting to avoid API limits and timeouts
                time.sleep(1.0)  # 1 request per second
                
                # Get player career stats
                career_stats = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=60)
                all_dataframes = career_stats.get_data_frames()
            
                # Debug: Print info about available dataframes
                logger.debug(f"Number of dataframes available: {len(all_dataframes)}")
                for i, df in enumerate(all_dataframes):
                    logger.debug(f"DataFrame {i} columns: {df.columns.tolist()}")
                    if not df.empty:
                        logger.debug(f"DataFrame {i} sample data: {df.head(1).to_dict('records')}")
                
                # Use the first dataframe which should be SeasonTotalsRegularSeason
                season_totals = all_dataframes[0]
                
                # The season column might be named differently, let's check common names
                season_column = None
                possible_season_columns = ['SEASON_ID', 'Season', 'SEASON', 'season']
                
                for col in possible_season_columns:
                    if col in season_totals.columns:
                        season_column = col
                        break
                
                if season_column is None:
                    logger.error(f"No season column found in DataFrame 0. Available columns: {season_totals.columns.tolist()}")
                    return None
                
                # Filter for the specific season
                season_data = season_totals[season_totals[season_column] == season]
                
                if season_data.empty:
                    logger.warning(f"No stats found for player {player_id} in season {season}")
                    logger.debug(f"Available seasons for player {player_id}: {season_totals[season_column].unique()}")
                    return None
                    
                # Get the first row (should only be one)
                stats = season_data.iloc[0]
                
                return {
                    'games_played': stats.get('GP'),
                    'games_started': stats.get('GS'),
                    'total_minutes': stats.get('MIN'),
                    'total_field_goals_made': stats.get('FGM'),
                    'total_field_goals_attempt': stats.get('FGA'),
                    'total_threes_goals_made': stats.get('FG3M'),
                    'total_threes_goals_attempt': stats.get('FG3A'),
                    'total_free_throws_made': stats.get('FTM'),
                    'total_free_throws_attempt': stats.get('FTA'),
                    'total_offensive_rebounds': stats.get('OREB'),
                    'total_defensive_rebounds': stats.get('DREB'),
                    'total_rebounds': stats.get('REB'),
                    'total_assists': stats.get('AST'),
                    'total_steals': stats.get('STL'),
                    'total_blocks': stats.get('BLK'),
                    'total_turnovers': stats.get('TOV'),
                    'total_personal_fouls': stats.get('PF'),
                    'total_points': stats.get('PTS')
                }
            
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # Progressive backoff: 5s, 10s, 15s
                    logger.warning(f"Attempt {attempt + 1} failed for player {player_id} season {season}: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"All {max_retries} attempts failed for player {player_id} season {season}: {e}")
                    return None
        
        return None

    async def insert_player_stats(self, session: AsyncSession, players_teams_id: int, stats: Dict):
        """Insert player stats into RegularSeasonStats table."""
        try:
            regular_season_stat = RegularSeasonStats(
                players_teams_id=players_teams_id,
                **stats
            )
            
            session.add(regular_season_stat)
            await session.commit()
            
        except Exception as e:
            logger.error(f"Error inserting stats for players_teams_id {players_teams_id}: {e}")
            await session.rollback()
            raise e

    async def populate_stats(self, limit: Optional[int] = None):
        """Main function to populate regular season stats."""
        logger.info("Starting regular season stats population...")
        
        async with async_session() as session:
            try:
                # Get all player-team associations needing stats
                associations = await self.get_player_teams_associations(session)
                
                if not associations:
                    logger.info("No associations found that need stats populated")
                    return
                
                # Limit processing if specified
                if limit:
                    associations = associations[:limit]
                    logger.info(f"Processing limited to {limit} associations")
                
                total_associations = len(associations)
                
                for i, assoc in enumerate(associations, 1):
                    try:
                        logger.info(
                            f"Processing {i}/{total_associations}: "
                            f"{assoc['player_name']} ({assoc['team_abbreviation']}) - {assoc['season']} "
                            f"(players_teams_id: {assoc['players_teams_id']})"
                        )
                        
                        # Get player stats from NBA API
                        stats = self.get_player_season_stats(assoc['player_id'], assoc['season'])
                        
                        if stats is None:
                            logger.warning(f"Skipping {assoc['player_name']} - no stats available")
                            self.skipped_count += 1
                            continue
                        
                        # Insert stats into database
                        await self.insert_player_stats(session, assoc['players_teams_id'], stats)
                        
                        self.processed_count += 1
                        logger.info(f"Successfully processed {assoc['player_name']}")
                        
                        # Progress update every 10 players
                        if i % 10 == 0:
                            success_rate = (self.processed_count / i) * 100 if i > 0 else 0
                            logger.info(f"Progress: {i}/{total_associations} processed. Success rate: {success_rate:.1f}%")
                            
                    except Exception as e:
                        logger.error(f"Error processing {assoc['player_name']} (players_teams_id: {assoc['players_teams_id']}): {e}")
                        self.error_count += 1
                        continue
                
            except Exception as e:
                logger.error(f"Fatal error in populate_stats: {e}")
                raise e

    def print_summary(self):
        """Print summary of the population process."""
        logger.info("=" * 50)
        logger.info("POPULATION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Successfully processed: {self.processed_count}")
        logger.info(f"Skipped (no data): {self.skipped_count}")
        logger.info(f"Errors: {self.error_count}")
        logger.info(f"Total attempted: {self.processed_count + self.skipped_count + self.error_count}")


async def main():
    """Main function to run the population script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate RegularSeasonStats table')
    parser.add_argument('--limit', type=int, help='Limit number of associations to process (for testing)')
    parser.add_argument('--dry-run', action='store_true', help='Run without actually inserting data')
    
    args = parser.parse_args()
    
    # Enable debug logging for small test runs to see what's happening
    if args.limit and args.limit <= 5:
        logging.getLogger().setLevel(logging.DEBUG)
    
    populator = RegularSeasonStatsPopulator()
    
    try:
        if args.dry_run:
            logger.info("DRY RUN MODE - No data will be inserted")
            # Just get associations and print info
            async with async_session() as session:
                associations = await populator.get_player_teams_associations(session)
                logger.info(f"Would process {len(associations)} associations")
                if associations:
                    logger.info("First few associations:")
                    for assoc in associations[:5]:
                        logger.info(f"  - {assoc['player_name']} ({assoc['team_abbreviation']}) - {assoc['season']}")
        else:
            await populator.populate_stats(limit=args.limit)
        
        populator.print_summary()
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        populator.print_summary()
    except Exception as e:
        logger.error(f"Script failed: {e}")
        populator.print_summary()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())