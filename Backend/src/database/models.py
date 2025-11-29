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
    city = Column(String, nullable=False)
    conference = Column(String, nullable=False)
    year_founded = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<Team(id={self.id}, full_name='{self.full_name}', abbreviation='{self.abbreviation}', city='{self.city}', conference='{self.conference}', year_founded={self.year_founded})>"
    

class Players(Base):
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    height = Column(String, nullable=True)
    weight = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=False)

    team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=True)
    jersey_number = Column(String, nullable=True)
    position = Column(String, nullable=True)
    draft_year = Column(Integer, nullable=False)
    school = Column(String, nullable=True)

    team = relationship("Teams", back_populates="players")

    def __repr__(self):
        return f"<Player(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', team_id={self.team_id}, position='{self.position}', height='{self.height}', weight={self.weight}, birth_date={self.birth_date})>"