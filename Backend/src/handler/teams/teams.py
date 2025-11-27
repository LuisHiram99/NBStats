from fastapi import APIRouter, Depends, HTTPException, Request
from . import service



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