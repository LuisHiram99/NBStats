from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from . import service
from ..rate_limiter import limiter
from auth.auth import get_current_user



from db import models, schemas
from db.database import get_db

router = APIRouter(prefix="/me", tags=["current_user"])

user_dependency = Annotated[dict, Depends(get_current_user)]

# ---------------- Current user's info endpoints ----------------

@router.get("/", response_model=schemas.UserResponse)
@limiter.limit("15/minute")
async def read_current_user(request: Request, user: user_dependency, db: AsyncSession = Depends(get_db)):
    """
    Get the currently authenticated user
    """
    return await service.get_user_info(user, db)

@router.patch("/", response_model=schemas.UpdateUserRequest)
@limiter.limit("15/minute")
async def patch_current_user(
    request: Request,
    current_user: user_dependency,
    user: schemas.UpdateUserRequest,           
    db: AsyncSession = Depends(get_db),
):
    """
    Partially update the currently authenticated user's information
    """
    return await service.patch_user_info(user, current_user, db)

@router.put("/password")
@limiter.limit("15/minute")
async def update_current_user_password(
    request: Request,
    current_user: user_dependency,
    password_update: schemas.UpdateUserPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update the currently authenticated user's password and return a new token.
    This invalidates all existing tokens by incrementing the token version.
    """
    return await service.update_user_password(password_update, current_user, db)

@router.delete("/", response_model=schemas.UserResponse)
@limiter.limit("15/minute")
async def delete_current_user(request: Request, user: user_dependency, db: AsyncSession = Depends(get_db)):
    """
    Delete the currently authenticated user
    """
    return await service.delete_user(user, db)

# ---------------- End of current user's info endpoints ----------------


