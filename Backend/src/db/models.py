from sqlalchemy import Column, Float, ForeignKey, Integer, String, PrimaryKeyConstraint, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from .database import Base
import enum

class Teams(Base):
    __tablename__ = 'teams'

    team_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    abbreviation = Column(String, nullable=False, unique=True)
    nickname = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=True)
    conference = Column(String, nullable=False)
    year_founded = Column(Integer, nullable=True)
    logo = Column(String, nullable=True)

    def __repr__(self):
        return f"<Team(id={self.id}, full_name='{self.full_name}', abbreviation='{self.abbreviation}', city='{self.city}', conference='{self.conference}', year_founded={self.year_founded})>"
    

class Players(Base):
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, nullable=False)
    position = Column(String, nullable=True)
    height = Column(String, nullable=True)
    weight = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=False)
    school = Column(String, nullable=True)
    rookie_season = Column(Integer, nullable=False)
    


    def __repr__(self):
        return f"<Player(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', team_id={self.team_id}, position='{self.position}', height='{self.height}', weight={self.weight}, birth_date={self.birth_date})>"
    
class PlayerTeamsAssociation(Base):
    __tablename__ = 'player_teams_association'

    players_teams_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.player_id'))
    team_id = Column(Integer, ForeignKey('teams.team_id'))
    season = Column(String, nullable=False)


class Games(Base):
    __tablename__ = 'games'

    game_id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    home_team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False)
    home_team_score = Column(Integer, nullable=True)
    away_team_score = Column(Integer, nullable=True)
    season = Column(String, nullable=False)

    home_team = relationship("Teams", foreign_keys=[home_team_id])
    away_team = relationship("Teams", foreign_keys=[away_team_id])

    def __repr__(self):
        return f"<Game(id={self.id}, date={self.date}, home_team_id={self.home_team_id}, away_team_id={self.away_team_id}, home_team_score={self.home_team_score}, away_team_score={self.away_team_score}, season='{self.season}')>"