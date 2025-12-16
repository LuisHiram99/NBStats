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

class PlayerBase(BaseModel):
    player_name: str
    position: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    birth_date: datetime
    school: Optional[str] = None
    rookie_season: int

class PlayerResponse(PlayerBase):
    player_id: int

    class Config:
        from_attributes = True

class PlayerCreate(PlayerBase):
    player_id: int

class PlayerUpdate(PlayerBase):
    pass