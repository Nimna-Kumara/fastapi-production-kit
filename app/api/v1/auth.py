from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.core.security import create_access_token


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user account."""
    return await UserService(db).create(data)

@router.post("/token", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """OAuth2 password grant — returns JWT access token."""
    user = await UserService(db).authenticate(form.username, form.password)
    token = create_access_token(subject=user.id)
    return Token(access_token=token)
