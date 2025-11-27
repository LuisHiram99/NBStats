from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

from handler.teams import teams

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
# TODO

api_route = "/api/v1"

app.include_router(teams.router, prefix=api_route, tags=["teams"])


@app.get("/")
async def root():
    return {"message": "Welcome to NBStats API!"}