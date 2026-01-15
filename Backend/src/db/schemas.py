from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime


# ------------------ User Schemas ------------------ #
class UserBase(BaseModel):
    username: str 
    email: str
    role: Optional[str] = None

class UserResponse(UserBase):  
    id: int
    username: str 
    email: str
    role: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CreateUserRequest(BaseModel):
    email: EmailStr = Field(..., max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=10, max_length=100)

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Must contain number')
        if not any(c in '!@#$%^&*' for c in v):
            raise ValueError('Must contain special character')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john@example.com",
                "username": "johndoe",
                "password": "Secretpassword1!"
            }
        }
    }

class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = Field(None, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)

class UpdateUserPasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=10, max_length=100)
    new_password: str = Field(..., min_length=10, max_length=100)

    @field_validator('new_password')
    @classmethod
    def validate_new_password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Must contain number')
        if not any(c in '!@#$%^&*' for c in v):
            raise ValueError('Must contain special character')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "current_password": "Oldpassword1!",
                "new_password": "Newsecurepassword2@"
            }
        }
    }

# ------------------ Team Schemas ------------------ #
class TeamBase(BaseModel):
    full_name: str
    abbreviation: str
    nickname: str
    city: str
    state: Optional[str] = None
    conference: str
    year_founded: Optional[int] = None
    logo: Optional[str] = None

class TeamBasicInfoResponse(BaseModel):
    team_id: int
    full_name: str
    abbreviation: str
    logo: Optional[str] = None

    class Config:
        from_attributes = True

class TeamResponse(TeamBase):
    team_id: int
    
    class Config:
        from_attributes = True

class TeamCreate(TeamBase):
    team_id: int

class TeamUpdate(TeamBase):
    pass

# ------------------ Player Schemas ------------------ #
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

# ------------------ Player-Team Association Schemas ------------------ #
class PlayerTeamAssociationBase(BaseModel):
    player_id: int
    team_id: int
    season: str 
    
class PlayerTeamAssociationResponse(PlayerTeamAssociationBase):
    players_teams_id: int

    class Config:
        from_attributes = True

class FavoriteTeamsRequest(BaseModel):
    team_ids: List[int]
    
class PlayerTeamAssociationCreate(PlayerTeamAssociationBase):
    players_teams_id: int

class PlayerTeamAssociationUpdate(PlayerTeamAssociationBase):
    pass