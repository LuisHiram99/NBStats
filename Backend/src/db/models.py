from sqlalchemy import Column, Float, ForeignKey, Integer, String, PrimaryKeyConstraint, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from .database import Base
import enum

class UserRole(enum.Enum):
    user = "user"
    admin = "admin"

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(
        PGEnum(UserRole, name="user_roles", create_type=True),
        nullable=False, default=UserRole.user,
    )
    token_version = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

class Teams(Base):
    __tablename__ = 'teams'

    team_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
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
    
class UsersTeamsAssociation(Base):
    """
    Association table between Users and Teams (so users can track favorite teams).
    """
    __tablename__ = 'users_teams_association'
    users_teams_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    team_id = Column(Integer, ForeignKey('teams.team_id'))

class Players(Base):
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    player_name = Column(String, nullable=False)
    position = Column(String, nullable=True)
    height = Column(String, nullable=True)
    weight = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=False)
    school = Column(String, nullable=True)
    rookie_season = Column(Integer, nullable=False)
    


    def __repr__(self):
        return f"<Player(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', team_id={self.team_id}, position='{self.position}', height='{self.height}', weight={self.weight}, birth_date={self.birth_date})>"
    
class UserPlayersAssociation(Base):
    """
    Association table between Users and Players (so users can track favorite players).
    """
    __tablename__ = 'user_players_association'
    users_players_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    player_id = Column(Integer, ForeignKey('players.player_id'))
    
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
    
class RegularSeasonStats(Base):
    __tablename__ = 'regular_season_stats'

    stats_id = Column(Integer, primary_key=True, index=True)
    players_teams_id = Column(Integer, ForeignKey('player_teams_association.players_teams_id'))

    games_played = Column(Integer, nullable=True)
    games_started = Column(Integer, nullable=True)
    total_minutes = Column(Integer, nullable=True)
    total_field_goals_made = Column(Integer, nullable=True)
    total_field_goals_attempt = Column(Integer, nullable=True)
    total_threes_goals_made = Column(Integer, nullable=True)
    total_threes_goals_attempt = Column(Integer, nullable=True)
    total_free_throws_made = Column(Integer, nullable=True)
    total_free_throws_attempt = Column(Integer, nullable=True)
    total_offensive_rebounds = Column(Integer, nullable=True)
    total_defensive_rebounds = Column(Integer, nullable=True)
    total_rebounds = Column(Integer, nullable=True)
    total_assists = Column(Integer, nullable=True)
    total_steals = Column(Integer, nullable=True)
    total_blocks = Column(Integer, nullable=True)
    total_turnovers = Column(Integer, nullable=True)
    total_personal_fouls = Column(Integer, nullable=True)
    total_points = Column(Integer, nullable=True)

    # Relationship to PlayerTeamsAssociation
    player_team_association = relationship("PlayerTeamsAssociation", backref="regular_season_stats")

    def __repr__(self):
        return f"<RegularSeasonStats(id={self.id}, player_id={self.player_id}, season='{self.season}', games_played={self.games_played}, points_per_game={self.points_per_game}, rebounds_per_game={self.rebounds_per_game}, assists_per_game={self.assists_per_game}, steals_per_game={self.steals_per_game}, blocks_per_game={self.blocks_per_game})>"