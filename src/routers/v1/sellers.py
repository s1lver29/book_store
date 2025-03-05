from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.seller import Seller
from src.schemas.sellers import SellerCreate, SellerReturn, SellerWithBooks, SellerBase
from src.config.connection_db import async_database_session

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

DBSession = Annotated[AsyncSession, Depends(async_database_session)]


@sellers_router.post(
    "/", response_model=SellerReturn, status_code=status.HTTP_201_CREATED
)
async def create_seller(
    seller: SellerCreate,
    session: DBSession,
):
    new_seller = Seller(**seller.model_dump())
    session.add(new_seller)
    await session.commit()
    await session.refresh(new_seller)
    return new_seller


@sellers_router.get("/", response_model=list[SellerReturn])
async def get_all_sellers(
    session: DBSession,
):
    result = await session.execute(select(Seller))
    sellers = result.scalars().all()
    return sellers


@sellers_router.get("/{seller_id}", response_model=SellerWithBooks)
async def get_seller(
    seller_id: int,
    session: DBSession,
):
    result = await session.execute(select(Seller).where(Seller.id == seller_id))
    seller = result.scalars().first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    await session.refresh(seller, attribute_names=["books"])

    return seller


@sellers_router.put("/{seller_id}", response_model=SellerReturn)
async def update_seller(
    seller_id: int,
    seller_update: SellerBase,
    session: DBSession,
):
    result = await session.execute(select(Seller).where(Seller.id == seller_id))
    seller = result.scalars().first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    seller.first_name = seller_update.first_name
    seller.last_name = seller_update.last_name
    seller.e_mail = seller_update.e_mail

    await session.commit()
    await session.refresh(seller)
    return seller


@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(
    seller_id: int,
    session: DBSession,
):
    result = await session.execute(select(Seller).where(Seller.id == seller_id))
    seller = result.scalars().first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    await session.delete(seller)
    await session.commit()
    return None
