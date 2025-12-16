from nba_api.stats.endpoints import playercareerstats
import matplotlib.pyplot as plt
from nba_api.stats.static import players
import seaborn as sns
import pandas as pd
from json import loads, dumps
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats
import time


pd.set_option("display.max_columns", None)

from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import commonteamroster
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import playerdashboardbyyearoveryear
from nba_api.stats.endpoints import playergamelog
from helpfuncs import get_current_season

eastern_conference = {
    'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DET', 'IND',
    'MIA', 'MIL', 'NYK', 'ORL', 'PHI', 'TOR', 'WAS'
}

western_conference = {
    'DAL', 'DEN', 'GSW', 'HOU', 'LAC', 'LAL', 'MEM', 'MIN',
    'NOP', 'OKC', 'PHX', 'POR', 'SAC', 'SAS', 'UTA'
}

teams_list = list(eastern_conference.union(western_conference))

class player():
    def get_player_info(self, player_id:int) -> pd.DataFrame:
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        info_df = player_info.get_data_frames()[0]
        return info_df
    
    def get_player_latest_performance(self, player_id:int) -> pd.Series | str:
        game_log = playergamelog.PlayerGameLog(
            player_id=player_id,
            season=get_current_season()
        )
        df = game_log.get_data_frames()[0]

        if df.empty:
            return "Player is not active this season or has not played any games."
        return df.iloc[0]

    def get_alltime_player_stats(self, player_id:int) -> pd.DataFrame:
        career = playercareerstats.PlayerCareerStats(player_id=player_id)
        career_df = career.get_data_frames()[0]

        return career_df

    def get_current_season_stats(self, player_id:int) -> pd.DataFrame:
        player_dashboard = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(
            player_id=player_id,
            season=get_current_season()
        )

        current_stats = player_dashboard.get_data_frames()[0]
        current_stats = current_stats[["GP", "MIN", "FG_PCT", "FG3_PCT", "FT_PCT", "REB", 
                                    "AST", "PTS", "BLK", "PLUS_MINUS"]]
        current_stats["PPG"] = round(current_stats["PTS"] / current_stats["GP"], 2)
        current_stats["APG"] = round(current_stats["AST"] / current_stats["GP"], 2)
        current_stats["RPG"] = round(current_stats["REB"] / current_stats["GP"], 2)
        current_stats["BPG"] = round(current_stats["BLK"] / current_stats["GP"], 2)
        current_stats["MPG"] = round(current_stats["MIN"] / current_stats["GP"], 2) 
        current_stats
        return current_stats


    def plot_stat_over_career(self, player_id, stat):
        player_name = players.find_player_by_id(player_id)
        career_df = self.get_alltime_player_stats(player_id=player_id)
        if stat not in career_df.columns:
            raise ValueError(f"Stat '{stat}' not found in career data.")
        
        print(player_name)
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=career_df, x='SEASON_ID', y=stat, marker='o')
        plt.title(f"{player_name['full_name']}'s {stat} Over Career")
        plt.xlabel('Season')
        plt.ylabel(stat)
        plt.xticks(rotation=45)
        plt.grid() 
        plt.show()


    def get_rookie_season(self, player_id:int) -> str:
        career = playercareerstats.PlayerCareerStats(player_id=player_id)
        career_df = career.get_data_frames()[0]
        if career_df.empty:
            return get_current_season()
        rookie_season = career_df.iloc[0]['SEASON_ID']
        return rookie_season

    def get_team_roster_per_season(self, teamAbbreviation:str, season:str = get_current_season()) -> pd.DataFrame:
        team_details = teams.find_team_by_abbreviation(teamAbbreviation)
        team_id = team_details["id"]
        roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
        roster_data = roster.get_data_frames()[0]
        current_season = get_current_season()
        
        rookie_seasons = []
        for _, row in roster_data.iterrows():
            if row['EXP'] == 'R':
                rookie_season = current_season
            else: 
                rookie_season = self.get_rookie_season(row['PLAYER_ID'])
            rookie_seasons.append(rookie_season)
            time.sleep(0.6)  # To avoid hitting rate limits

        roster_data['ROOKIE_SEASON'] = rookie_seasons

        roster_data.drop(columns=['TeamID', 'SEASON', 'LeagueID', 'EXP', 'AGE', 'NUM', 'HOW_ACQUIRED', 'PLAYER_SLUG', 'NICKNAME'], inplace=True, axis=1)
        roster_data.set_index('PLAYER_ID', drop=True, inplace=True)
        return roster_data