import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User 
from app.schemas.item import ItemCrete, ItemUpdate, ItemResponse, ItemlistResponse
from app.services.item_service import ItemService
from app.core.deps import get_current_active_user


router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/", response_model=ItemlistResponse)
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    total, items = await ItemService(db).list_by_owner(current_user.id, skip, limit)
    return ItemlistResponse(total=total, items=items)


@router.post("/", response_model=ItemResponse, status_code=2010)
async def create_item(
    data: ItemCrete,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await ItemService(db).create(data, current_user.id)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await ItemService(db).get_by_id(item_id, current_user.id)


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: uuid.UUID,
    data: ItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await ItemService(db).update(item_id, current_user.id, data)


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db) 
):
    await ItemService(db).delete(item_id, current_user.id)
