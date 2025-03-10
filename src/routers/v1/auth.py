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
    """
    Логин пользователя и получение токена доступа.

    Эта функция проверяет имя пользователя и пароль, переданные в форме, и если они верны,
    генерирует токен доступа с использованием JWT.
    В случае некорректных данных возвращает ошибку 401.

    Параметры
    ----------
    form_data : OAuth2PasswordRequestForm
        Данные формы с именем пользователя (e_mail) и паролем, переданные пользователем.

    session : AsyncSession
        Сессия базы данных для выполнения запросов.

    Возвращаемое значение
    ---------------------
    dict
        Словарь с токеном доступа и типом токена.

    Исключения
    -----------
    HTTPException
        В случае неверных данных пользователя (неправильный email или пароль)
        будет поднято исключение 401 Unauthorized с сообщением об ошибке.

    Пример
    -------
    Пример успешного ответа:

    {
        "access_token": "some_jwt_token",
        "token_type": "bearer"
    }

    Пример ошибки (неправильный email или пароль):

    HTTP 401 Unauthorized
    {
        "detail": "Incorrect email or password"
    }
    """
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
