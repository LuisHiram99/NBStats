from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from db import models, schemas
from auth.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, pwd_context, email_exists, username_exists

# ----------------------Service functions for current user operations ----------------------
async def get_user_info(user: dict, db: AsyncSession) -> schemas.UserResponse:
    """Retrieve current user information from the database."""
    try: 
        result = await db.execute(select(models.Users).where(models.Users.id == user['user_id']))
        user_record = result.scalar_one_or_none()
        if not user_record:
            raise HTTPException(status_code=404, detail="User not found")
        return user_record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def patch_user_info(
    user_update: schemas.UpdateUserRequest,
    current_user: dict,
    db: AsyncSession
) -> schemas.UpdateUserRequest:
    """Partially update current user's information."""
    try:
        result = await db.execute(select(models.Users).where(models.Users.id == current_user['user_id']))
        user_record = result.scalar_one_or_none()
        if not user_record:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check for email or username conflicts
        if user_update.email and user_update.email != user_record.email:
            if await email_exists(user_update.email, db):
                raise HTTPException(status_code=400, detail="Email already in use")
        
        if user_update.username and user_update.username != user_record.username:
            if await username_exists(user_update.username, db):
                raise HTTPException(status_code=400, detail="Username already in use")
        
        for var, value in vars(user_update).items():
            if value is not None:
                setattr(user_record, var, value)
        
        db.add(user_record)
        await db.commit()
        await db.refresh(user_record)
        return user_record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def update_user_password(
        password_update: schemas.UpdateUserPasswordRequest,
        current_user: dict,
        db: AsyncSession
) -> dict:
    """
    Update current user's password and increment token version to invalidate existing tokens.
    """
    try:
        result = await db.execute(select(models.Users).where(models.Users.id == current_user['user_id']))
        user_record = result.scalar_one_or_none()

        if user_record is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify current password
        if not pwd_context.verify(password_update.current_password, user_record.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update to new password
        user_record.hashed_password = pwd_context.hash(password_update.new_password)
        user_record.token_version += 1  # Invalidate existing tokens

        db.add(user_record)
        await db.commit()
        await db.refresh(user_record)

        # Create new access token
        new_token = create_access_token(
            email=user_record.email,
            user_id=user_record.id,
            token_version=user_record.token_version,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 
        )

        return {
            "message": "Password updated successfully, please use the new token for authentication.",
            "access_token": new_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while updating password: " + str(e))

async def delete_user(
        user: dict,
        db: AsyncSession
) -> schemas.UserResponse:
    """
    Deletes current logged-in user
    """
    try:
        result = await db.execute(select(models.Users)
                            .where(models.Users.id == user['user_id']))
        user_record = result.scalars().first()

        if user_record is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        await db.delete(user_record)
        await db.commit()
        return {'message': "User deleted succesfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while deleting user: " + str(e))

