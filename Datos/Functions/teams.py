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
from .games import get_current_standings

eastern_conference = {
    'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DET', 'IND',
    'MIA', 'MIL', 'NYK', 'ORL', 'PHI', 'TOR', 'WAS'
}

western_conference = {
    'DAL', 'DEN', 'GSW', 'HOU', 'LAC', 'LAL', 'MEM', 'MIN',
    'NOP', 'OKC', 'PHX', 'POR', 'SAC', 'SAS', 'UTA'
}

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
    def __init__(self, team_abbreviation: str = None, team_id:str = None, team_name:str = None):
        self.current_season = get_current_season()
        provided = [
            team_abbreviation is not None,
            team_id is not None,
            team_name is not None
        ]

        if sum(provided) != 1:
            raise ValueError("You must provide exactly one of: team_abbreviation, team_id, team_name")

        # buscar por el parámetro correcto
        if team_abbreviation is not None:
            self.team_details = self.get_team_details_by_abbreviation(team_abbreviation)

        elif team_id is not None:
            self.team_details = self.get_team_details_by_id(team_id)

        elif team_name is not None:
            self.team_details = self.get_team_details_by_name(team_name)

        # añadir conferencia
        if not self.team_details:
            raise ValueError("Team not found with the provided identifier.")
        abb = self.team_details["abbreviation"]
        self.team_details["conference"] = "East" if abb in eastern_conference else "West"


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

    def get_all_teams(self) -> pd.DataFrame:
        try:
            all_teams = teams.get_teams()
            teams_df = pd.DataFrame(all_teams)
            return teams_df.to_json(orient="records")
        except Exception as e:
            print(f"Error retrieving all teams: {e}")
            raise e
    
    def get_team_details(self) -> Dict:
        try:
            return self.team_details
        except Exception as e:
            print(f"Error retrieving team details for abbreviation {self.team_abbreviation}: {e}")
            raise e

    def get_team_details_by_abbreviation(self, team_abbreviation:str) -> Dict:
        try:
            team_details = teams.find_team_by_abbreviation(team_abbreviation)
            return team_details
        except Exception as e:
            print(f"Error retrieving team details for abbreviation {team_abbreviation}: {e}")
            raise e
    
    def get_team_details_by_id(self, team_id:int) -> Dict:
        try:
            team_details = teams.find_team_name_by_id(team_id)
            return team_details
        except Exception as e:
            print(f"Error retrieving team details for ID {team_id}: {e}")
            raise e
        
    def get_team_details_by_name(self, team_name:str) -> Dict:
        try:
            team_details = teams.find_teams_by_full_name(team_name)[0]
            return team_details
        except Exception as e:
            print(f"Error retrieving team details for name {team_name}: {e}")
            raise e

    def get_team_roster_per_season(self, season:str = None) -> pd.DataFrame:
        try:
            season = self.check_valid_season(season)

            team_id = self.team_details["id"]
            roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
            roster_data = roster.get_data_frames()[0]
            roster_data = roster_data[["PLAYER", "NUM", "POSITION", "HEIGHT", "WEIGHT", "BIRTH_DATE", "AGE", "EXP", "SCHOOL"]]
            return roster_data
        except Exception as e:
            print(f"Error retrieving roster for team {self.team_details['abbreviation']} in season {season}: {e}")
            raise e

    def get_team_last_n_games_played(self, season:str = None, last_n_games:int = 5) -> pd.DataFrame:
        season = self.check_valid_season(season)
        team_details = self.team_details
        team_id = team_details["id"]
        game_log = teamgamelog.TeamGameLog(team_id=team_id, season=season)
        game_log = game_log.get_data_frames()[0]

        game_log = game_log[['Game_ID', 'GAME_DATE', 'MATCHUP', 'WL']]
        return game_log[:last_n_games]
    
    def get_team_league_standing(self, season:str = None) -> pd.DataFrame:
        season = self.check_valid_season(season)
        standings = get_current_standings(conference=self.team_details['conference']).reset_index()
        index = int(standings[standings['TeamName'] == self.team_details['nickname']].index[0]) + 1

        return index
    

    def get_team_full_info(self, season:str = None):
        pass



        
    