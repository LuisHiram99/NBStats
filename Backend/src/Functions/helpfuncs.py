from datetime import datetime


def get_current_season():
    """Get current NBA season in the format 'YYYY-YY'"""
    today = datetime.now()
    year = today.year
    month = today.month
    
    # NBA season typically starts in October
    # If current month is before October, we're in the second half of the season
    if month < 10:
        season_start = year - 1
    else:
        season_start = year
    
    season_end = str(season_start + 1)[-2:]  # Get last 2 digits
    return f"{season_start}-{season_end}"