from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.connection_db import async_database_session
from src.config.settings import settings
from src.models.seller import Seller

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


def verify_password(plain_password, hashed_password):
    """
    Проверяет, что обычный пароль совпадает с захешированным.

    Параметры
    ----------
    plain_password : str
        Обычный текст пароля для проверки.
    hashed_password : str
        Захешированный пароль, с которым будет произведена проверка.

    Возвращает
    -------
    bool
        True, если обычный пароль совпадает с захешированным, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta):
    """
    Создаёт JWT токен с указанными данными и временем истечения.

    Параметры
    ----------
    data : dict
        Данные, которые будут включены в токен.
    expires_delta : timedelta
        Время жизни токена.

    Возвращает
    -------
    str
        Закодированный JWT токен.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(async_database_session),
):
    """
    Получает текущего пользователя по токену.

    Параметры
    ----------
    token : str
        JWT токен, содержащий информацию о пользователе.
    session : AsyncSession
        Сессия для работы с базой данных.

    Возвращает
    -------
    Seller
        Объект пользователя, если токен действителен, иначе вызывает исключение.

    Исключения
    -----------
    HTTPException
        Если токен недействителен или пользователь не найден, генерируется исключение 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await session.execute(select(Seller).where(Seller.e_mail == email))
    seller = result.scalars().first()
    if seller is None:
        raise credentials_exception
    return seller
