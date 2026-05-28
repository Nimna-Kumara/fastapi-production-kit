import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.models.item import Item
from app.schemas.item import ItemCrete, ItemUpdate


class ItemService:
    def __init_(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, item_id: uuid.UUID, owner_id: uuid.UUID) -> Item:
        result = await self.db.execute(
            select(Item).where(Item.id == item_id, Item.owner_id == owner_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        return item

    async def create(self,  data: ItemCrete, owner_id: uuid.UUID) -> Item:
        item = Item(**data.model_dump(), owner_id=owner_id)
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def update(self, item_id: uuid.UUID, owner_id: uuid.UUID, data: ItemUpdate) -> Item:
        item = await self.get_by_id(item_id, owner_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete(self, item_id: uuid.UUID, owner_id: uuid.UUID) -> None:
        item = await self.get_by_id(item_id, owner_id)
        await self.db.delete(item)

    async def list_by_owner(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 20) -> tuple[int, list[Item]]:
        q = select(Item).where(Item.owner_id == owner_id)
        total = (await self.db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        result = await self.db.execute(q.offset(skip).limit(limit))
        return total, result.scalars().all()
