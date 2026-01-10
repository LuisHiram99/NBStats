import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.database import async_session
from db.models import Players, Teams, PlayerTeamsAssociation, RegularSeasonStats
from handler.players

# NBA API imports
from nba_api.stats.endpoints import playercareerstats, playerprofilev2
import pandas as pd
import time