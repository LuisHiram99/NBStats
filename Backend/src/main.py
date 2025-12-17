from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from pathlib import Path
from fastapi.staticfiles import StaticFiles


from handler.teams import teams
from handler.players import players
from handler.rate_limiter import limiter



app = FastAPI(
    title="NBStats",
    description="NBA app for getting high valuable stats",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Rate limiter: 
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add logo root endpoint:
logos_path = Path(__file__).parent / "logos"
logos_path.mkdir(exist_ok=True) 

app.mount("/logos", StaticFiles(directory=str(logos_path)), name="logos")

# Include routers
api_route = "/api/v1"

app.include_router(teams.router, prefix=api_route, tags=["teams"])
app.include_router(players.router, prefix=api_route, tags=["players"])


@app.get("/")
async def root():
    return {"message": "Welcome to NBStats API!"}