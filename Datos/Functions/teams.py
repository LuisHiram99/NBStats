from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.endpoints import commonteamroster
from datetime import datetime, timezone, timedelta
from dateutil import parser
from nba_api.live.nba.endpoints import scoreboard
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple, Union, Optional

def get_current_season():
    """Get current NBA season in the format 'YYYY-YY'"""
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

class Teams():
    def __init__(self):
        self.current_season = get_current_season()

    def check_valid_season(self, season: str) -> str:
        """Check if the provided season is valid and return formatted season."""
        if not season:
            season = self.current_season
        elif not season.isdigit():
            raise ValueError(f"Invalid season format: {season}. Expected a year in 'YYYY' format.")
        elif int(season) < 1980 or int(season) > datetime.now().year:
            raise ValueError(f"Invalid season year: {season}. Year must be between 1980 and {datetime.now().year}.")
        else:
            season = f"{season}-{str(int(season)+1)[-2:]}"
        
        return season

    def get_all_teams(self) -> List[Dict]:
        try:
            all_teams = teams.get_teams()
            return all_teams
        except Exception as e:
            print(f"Error retrieving all teams: {e}")
            raise e
    
    def get_team_details_by_abbreviation(self, teamAbbreviation:str) -> Dict:
        try:
            team_details = teams.find_team_by_abbreviation(teamAbbreviation)
            return team_details
        except Exception as e:
            print(f"Error retrieving team details for abbreviation {teamAbbreviation}: {e}")
            raise e
    
    def get_team_details_by_id(self, team_id:int) -> Dict:
        try:
            team_details = teams.find_team_name_by_id(team_id)
            return team_details
        except Exception as e:
            print(f"Error retrieving team details for ID {team_id}: {e}")
            raise e
        
    def get_team_by_name(self, team_name:str) -> List[Dict]:
        try:
            team_details = teams.find_teams_by_full_name(team_name)
            return team_details
        except Exception as e:
            print(f"Error retrieving team details for name {team_name}: {e}")
            raise e

    def get_team_roster_per_season(self, teamAbbreviation:str, season:str = None) -> List[Dict]:
        try:
            season = self.check_valid_season(season)

            team_details = teams.find_team_by_abbreviation(teamAbbreviation)
            team_id = team_details["id"]
            roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
            roster_data = roster.get_data_frames()[0]
            drop_cols = ['']
            roster_data = roster_data[["PLAYER", "NUM", "POSITION", "HEIGHT", "WEIGHT", "BIRTH_DATE", "AGE", "EXP", "SCHOOL"]]
            print(season)
            return roster_data.to_dict(orient="records")
        except Exception as e:
            print(f"Error retrieving roster for team {teamAbbreviation} in season {season}: {e}")
            raise e

    def get_team_games_played_per_season(self, season:str = None, teamAbbreviation:str = None) -> List[Dict]:
        season = self.check_valid_season(season)
        team_details = teams.find_team_by_abbreviation(teamAbbreviation)
        team_id = team_details["id"]
        game_log = teamgamelog.TeamGameLog(team_id=team_id, season=season)
        game_log = game_log.get_data_frames()[0]
        return game_log.to_dict(orient="records")
        
