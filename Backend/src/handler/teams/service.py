from fastapi import HTTPException, Request
import sys
from pathlib import Path

# Add NBStats root to path
nbstats_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(nbstats_root))

from Datos.Functions.teams import Teams

def get_all_teams():
    try:
        teams_data = Teams().get_all_teams()
        return teams_data
    except Exception as e:
        print(f"Error getting teams information: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
def get_team_by_abbreviation(abbrev):
    try:
        team_data = Teams().get_team_details_by_abbreviation(teamAbbreviation=abbrev)
        return team_data
    except Exception as e:
        print(f"Error getting teams information: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
def get_team_roster_by_abbrev(season, abbrev):
    try:
        team_data = Teams().get_team_roster_per_season(teamAbbreviation=abbrev, season=season)
        return team_data
    except Exception as e:
        print(f"Error getting teams information: {e}")
        raise HTTPException(status_code=500, detail=str(e))
