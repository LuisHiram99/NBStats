from fastapi import APIRouter, Depends, HTTPException, Request
from . import service
from db.static_data import populate_teams_table, clear_teams_table, update_teams_data, get_teams_from_db



router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}},
)


@router.get("/all")
def get_all_teams():
    return service.get_all_teams()

@router.get("/{abbrev}")
def get_team_by_abbreviation(abbrev):
    return service.get_team_by_abbreviation(abbrev=abbrev)

@router.get("/{abbrev}/roster/{season}")
def get_team_roster(abbrev, season):
    return service.get_team_roster_by_abbrev(abbrev=abbrev, season=season)


# Database management endpoints
@router.post("/database/populate")
async def populate_teams_database():
    """
    Populate the teams database with all NBA teams from the API.
    This will add all teams that don't already exist in the database.
    """
    try:
        result = await populate_teams_table()
        if result["success"]:
            return {
                "message": "Teams database population completed successfully",
                "data": result
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error populating teams database: {str(e)}")


@router.get("/database/list")
async def get_teams_from_database():
    """
    Get all teams currently stored in the database.
    """
    try:
        teams = await get_teams_from_db()
        teams_data = []
        for team in teams:
            teams_data.append({
                "team_id": team.team_id,
                "full_name": team.full_name,
                "abbreviation": team.abbreviation,
                "nickname": team.nickname,
                "city": team.city,
                "state": team.state,
                "conference": team.conference,
                "year_founded": team.year_founded,
                "logo": team.logo
            })
        
        # Group by conference
        east_teams = [t for t in teams_data if t["conference"] == "East"]
        west_teams = [t for t in teams_data if t["conference"] == "West"]
        
        return {
            "total_teams": len(teams_data),
            "eastern_conference": {
                "count": len(east_teams),
                "teams": east_teams
            },
            "western_conference": {
                "count": len(west_teams),
                "teams": west_teams
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving teams from database: {str(e)}")


@router.put("/database/update")
async def update_teams_database():
    """
    Update all teams in the database with fresh data from the NBA API.
    """
    try:
        result = await update_teams_data()
        if result["success"]:
            return {
                "message": "Teams database updated successfully",
                "data": result
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating teams database: {str(e)}")


@router.delete("/database/clear")
async def clear_teams_database():
    """
    Clear all teams from the database. Use with caution!
    """
    try:
        result = await clear_teams_table()
        if result["success"]:
            return {
                "message": "Teams database cleared successfully",
                "data": result
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing teams database: {str(e)}")