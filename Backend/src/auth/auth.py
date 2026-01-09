from datetime import timedelta, datetime, timezone
from typing import Annotated
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from db.database import get_db
from db.models import Users
from starlette import status
from secrets import token_hex
import os
from pathlib import Path
from db.schemas import CreateUserRequest

router = APIRouter(prefix="/auth", tags=["auth"])

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load environment variables from config/.env
env_path = PROJECT_ROOT / 'config' / '.env'
load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.getenv("SECRET_KEY", token_hex(32))
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 300000  # 300000 minutes = ~208 days
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Use argon2 for password hashing (using argon2-cffi backend)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str

db_dependency = Annotated[AsyncSession, Depends(get_db)]

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUserRequest, db: db_dependency, request: Request):
    client_ip = request.client.host
    create_user_model = Users(
        email=user.email,
        username=user.username,
        hashed_password=pwd_context.hash(user.password)
    )
    if await email_exists(user.email, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if await username_exists(user.username, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    db.add(create_user_model)
    await db.commit()
    await db.refresh(create_user_model)
    return {'message': 'User created successfully'}

@router.post("/login", response_model=Token)
async def login_for_access_token(db: db_dependency, request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    client_ip = request.client.host
    username = form_data.username
    password = form_data.password
    user = await authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user.email, user.id, user.token_version, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

async def authenticate_user(db: db_dependency, username: str, password: str):
    result = await db.execute(select(Users).where(Users.username == username))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(email: str, user_id: int, token_version: int, expires_delta: timedelta | None = None):
    encode = {"sub": email, "user_id": user_id, "token_version": token_version}
    expires = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: db_dependency):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        token_version: int = payload.get("token_version", 0)
        
        if email is None or user_id is None:
            raise credentials_exception
        
        # Load full user to include role for authorization checks
        result = await db.execute(select(Users).where(Users.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise credentials_exception
        
        # Verify token version matches current user's token version
        if user.token_version != token_version:
            raise credentials_exception
        
        # role is an Enum; expose as string value
        return {'email': user.email, 'user_id': user.id, 'role': getattr(user.role, 'value', user.role)}
    except JWTError:
        raise credentials_exception
    

async def admin_required(current_user = Depends(get_current_user)):
    '''
    Dependency to ensure the current user has admin role
    '''
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )
    return current_user


def is_admin(user: dict = Depends(get_current_user)):
    '''
    Check if the current user has admin role
    '''
    if user["role"] != "admin":
        return False
    return True

async def email_exists(email: str, db: db_dependency):
    '''
    Check if an email already exists in the database
    '''
    result = await db.execute(select(Users).where(Users.email == email))
    user = result.scalar_one_or_none()
    return user is not None

async def username_exists(username: str, db: db_dependency):
    '''
    Check if a username already exists in the database
    '''
    result = await db.execute(select(Users).where(Users.username == username))
    user = result.scalar_one_or_none()
    return user is not None