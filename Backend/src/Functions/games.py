from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import leaguestandingsv3
from datetime import datetime, timezone, timedelta
from dateutil import parser
from nba_api.live.nba.endpoints import scoreboard

# Import get_current_season with error handling for different import contexts
try:
    from .helpfuncs import get_current_season
except ImportError:
    # Fallback for when imported from outside package context
    try:
        from helpfuncs import get_current_season
    except ImportError:
        # Define a minimal version if helpfuncs module is not available
        def get_current_season():
            today = datetime.now()
            year = today.year
            month = today.month
            
            # NBA season typically starts in October
            # If current month is before October, we're in the second half of the season
            if month < 10:
                season_start = year - 1
            else:
                season_start = year
            
            season_end = str(season_start + 1)[-2:]  # Get last 2 digits
            return f"{season_start}-{season_end}"
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Union, Optional



def check_valid_season(season: Optional[str] = None) -> str:
    """Check if the provided season is valid and return formatted season."""
    if not season:
        season = get_current_season()
        return season
    
    # Check if season is already in YYYY-YY format
    if "-" in season and len(season) == 7:
        try:
            start_year = int(season.split("-")[0])
            if start_year < 1980 or start_year > datetime.now().year:
                raise ValueError(f"Invalid season year: {start_year}. Year must be between 1980 and {datetime.now().year}.")
            return season
        except ValueError:
            raise ValueError(f"Invalid season format: {season}. Expected 'YYYY-YY' or 'YYYY' format.")
    
    # Check if season is a 4-digit year
    elif season.isdigit() and len(season) == 4:
        year = int(season)
        if year < 1980 or year > datetime.now().year:
            raise ValueError(f"Invalid season year: {season}. Year must be between 1980 and {datetime.now().year}.")
        # Convert to YYYY-YY format
        season = f"{season}-{str(year + 1)[-2:]}"
        return season
    
    else:
        raise ValueError(f"Invalid season format: {season}. Expected 'YYYY-YY' or 'YYYY' format.")
    
    return season

def get_team_game_log( team_id: int, season: str) -> pd.DataFrame:
    game_log = teamgamelog.TeamGameLog(team_id=team_id, season=season)
    game_log = game_log.get_data_frames()[0]
    return game_log

def get_todays_games()-> None:
    f = "{gameId}: {awayTeam} @ {homeTeam} : {gameTimeLTZ}" 
    board = scoreboard.ScoreBoard()
    print("ScoreBoardDate: " + board.score_board_date)
    games = board.games.get_dict()
    for game in games:
        gameTimeLTZ = parser.parse(game["gameTimeUTC"]).replace(tzinfo=timezone.utc).astimezone(tz=None)
        #print(f.format(gameId=game['gameId'], awayTeam=game['awayTeam']['teamName'], homeTeam=game['homeTeam']['teamName'], gameTimeLTZ=gameTimeLTZ))

    return games


def get_current_standings(season: str = None, conference:str = 'Overall') -> pd.DataFrame:
    """Get current NBA standings for all teams"""
    conference_types = ['Overall','West','East']
    try:
        if conference in conference_types:
            season = check_valid_season(season)
            
            standings = leaguestandingsv3.LeagueStandingsV3(
                league_id='00',  # NBA
                season=season,
                season_type='Regular Season'
            )
            
            standings_df = standings.get_data_frames()[0]
            
            # Select relevant columns
            columns_to_keep = [
                'TeamID', 'TeamCity', 'TeamName', 'Conference','WINS', 'LOSSES', 'PlayoffRank', 
                'Record', "HOME","ROAD", "L10"
            ]
            
            standings_df = standings_df[columns_to_keep]

            if conference != 'Overall':
                return standings_df[standings_df['Conference'] == conference].reset_index(drop=True)
            else:
                return standings_df
        else:
            raise ValueError(f"Invalid conference type: {conference}. Expected one of {conference_types}.")    
    except Exception as e:
        print(f"Error retrieving standings for season {season}: {e}")
        raise e
