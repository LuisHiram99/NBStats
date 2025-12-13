# NBA Teams Database Integration

This document explains how to use the `get_all_teams()` function from the `teams.py` module to populate the database with NBA teams information.

## Files Modified/Created

1. **`Backend/src/db/static_data.py`** - New file with database population functions
2. **`Backend/src/db/models.py`** - Added missing relationship for Teams model
3. **`Backend/src/handler/teams/teams.py`** - Added database management endpoints
4. **`Backend/populate_teams.py`** - Standalone script for populating teams

## Available Functions

### Static Data Functions (`static_data.py`)

- **`populate_teams_table()`** - Populates teams table with NBA API data (async)
- **`get_teams_from_db()`** - Retrieves all teams from database (async)
- **`clear_teams_table()`** - Clears all teams from database (async)
- **`update_teams_data()`** - Updates existing teams with fresh API data (async)
- **`run_populate_teams()`** - Synchronous wrapper for populate_teams_table()
- **`run_clear_teams()`** - Synchronous wrapper for clear_teams_table()
- **`run_update_teams()`** - Synchronous wrapper for update_teams_data()

### API Endpoints (Added to `/api/v1/teams`)

- **POST `/database/populate`** - Populate teams database
- **GET `/database/list`** - Get all teams from database
- **PUT `/database/update`** - Update teams with fresh API data
- **DELETE `/database/clear`** - Clear all teams from database

## Usage Examples

### 1. Using the Standalone Script

```bash
cd Backend
python populate_teams.py
```

### 2. Using the Functions Directly

```python
from db.static_data import run_populate_teams

# Populate teams table
result = run_populate_teams()
print(f"Added {result['teams_added']} teams")
```

### 3. Using the API Endpoints

```bash
# Populate teams database
curl -X POST http://localhost:8000/api/v1/teams/database/populate

# Get all teams from database
curl http://localhost:8000/api/v1/teams/database/list

# Update teams with fresh data
curl -X PUT http://localhost:8000/api/v1/teams/database/update
```

### 4. Using in Async Context

```python
import asyncio
from db.static_data import populate_teams_table

async def main():
    result = await populate_teams_table()
    print(f"Teams added: {result['teams_added']}")

asyncio.run(main())
```

## Data Flow

1. **`get_all_teams()`** function fetches teams data from NBA API
2. **`get_team_details_by_abbreviation()`** enriches data with conference information
3. **`populate_teams_table()`** creates Team objects and saves them to database
4. Database stores teams with: ID, full name, abbreviation, nickname, city, state, conference, year founded

## Database Schema

The `Teams` table includes:
- `team_id` (Primary Key)
- `full_name` (e.g., "Los Angeles Lakers")
- `abbreviation` (e.g., "LAL")
- `nickname` (e.g., "Lakers")
- `city` (e.g., "Los Angeles")
- `state` (e.g., "CA")
- `conference` ("East" or "West")
- `year_founded` (e.g., 1947)

## Features

- **Duplicate Prevention**: Won't add teams that already exist
- **Conference Detection**: Automatically determines East/West conference
- **Error Handling**: Comprehensive error handling and reporting
- **Batch Operations**: Efficient database operations
- **API Integration**: Full REST API for team management

## Next Steps

After populating teams, you can:
1. Add player data using similar patterns
2. Fetch game data and link to teams
3. Build analytics on top of the team data
4. Create team-specific dashboards

## Troubleshooting

- Ensure NBA API is accessible
- Check database connection settings
- Verify all dependencies are installed
- Make sure the Python path includes the Datos/Functions directory