from fastapi import HTTPException, Request
import sys
from pathlib import Path
import json

# Add NBStats root to path
nbstats_root = Path(__file__).resolve().parents[4]
datos_path = nbstats_root / "Datos" / "Functions"
if str(datos_path) not in sys.path:
    sys.path.insert(0, str(datos_path))

from teams import get_all_teams as api_get_all_teams, get_team_details_by_abbreviation, get_team_roster_per_season

def get_all_teams():
    try:
        teams_data = api_get_all_teams()
        return json.loads(teams_data)
    except Exception as e:
        print(f"Error getting teams information: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
def get_team_by_abbreviation(abbrev):
    try:
        team_data = get_team_details_by_abbreviation(team_abbreviation=abbrev)
        return team_data
    except Exception as e:
        print(f"Error getting teams information: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
def get_team_roster_by_abbrev(season, abbrev):
    try:
        # Get team details first to get the team ID
        team_details = get_team_details_by_abbreviation(team_abbreviation=abbrev)
        team_data = get_team_roster_per_season(team_id=team_details['id'], season=season)
        return team_data.to_json(orient='records')
    except Exception as e:
        print(f"Error getting teams information: {e}")
        raise HTTPException(status_code=500, detail=str(e))
