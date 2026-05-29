import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User 
from app.schemas.user import UserResponse, UserUpdate, UserListResponse
from app.services.user_service import UserService
from app.core.deps import get_current_active_user, require_superuser


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Return currently authenticated user."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await UserService(db).update(current_user.id, data)


# Admin-only route
@router.get("/", response_model=UserListResponse, dependencies=[Depends(require_superuser)])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    total, users = await UserService(db).list_user(skip, limit)
    return UserListResponse(total=total, items=users)