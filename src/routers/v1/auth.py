from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.connection_db import async_database_session
from src.config.settings import settings
from src.middlewares.auth import create_access_token, verify_password
from src.models.seller import Seller

auth_router = APIRouter(tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


@auth_router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(async_database_session),
):
    result = await session.execute(select(Seller).where(Seller.e_mail == form_data.username))
    seller = result.scalars().first()
    if not seller or not verify_password(form_data.password, seller.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": seller.e_mail}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
