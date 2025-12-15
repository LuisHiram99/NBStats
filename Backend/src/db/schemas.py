from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TeamBase(BaseModel):
    full_name: str
    abbreviation: str
    nickname: str
    city: str
    state: Optional[str] = None
    conference: str
    year_founded: Optional[int] = None
    logo: Optional[str] = None


class TeamResponse(TeamBase):
    team_id: int
    
    class Config:
        from_attributes = True


class TeamCreate(TeamBase):
    team_id: int


class TeamUpdate(TeamBase):
    pass