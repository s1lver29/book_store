from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.connection_db import async_database_session
from src.middlewares.auth import get_current_user
from src.models.seller import Seller
from src.schemas.sellers import SellerBase, SellerCreate, SellerReturn, SellerWithBooks

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

DBSession = Annotated[AsyncSession, Depends(async_database_session)]
current_user = Annotated[Seller, Depends(get_current_user)]

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


@sellers_router.post("/", response_model=SellerReturn, status_code=status.HTTP_201_CREATED)
async def create_seller(
    seller: SellerCreate,
    session: DBSession,
):
    """
    Создание нового продавца.

    Эта функция позволяет создать нового продавца в системе, включая хеширование пароля.

    Параметры
    ----------
    seller : SellerCreate
        Данные для создания продавца, включая имя, фамилию, email и пароль.

    session : DBSession
        Сессия базы данных для выполнения операций с продавцами.

    Возвращаемое значение
    ---------------------
    SellerReturn
        Данные о созданном продавце, включая его ID и другую информацию.

    Пример
    -------
    Пример успешного ответа:

    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe@example.com"
    }
    """
    new_seller = Seller(**seller.model_dump())
    new_seller.password = pwd_context.hash(new_seller.password)

    session.add(new_seller)
    await session.commit()
    await session.refresh(new_seller)
    return new_seller


@sellers_router.get("/", response_model=list[SellerReturn])
async def get_all_sellers(
    session: DBSession,
):
    """
    Получение списка всех продавцов.

    Эта функция возвращает список всех продавцов в системе.

    Параметры
    ----------
    session : DBSession
        Сессия базы данных для выполнения запроса на получение продавцов.

    Возвращаемое значение
    ---------------------
    list[SellerReturn]
        Список всех продавцов в системе.

    Пример
    -------
    Пример успешного ответа:

    [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "e_mail": "john.doe@example.com"
        },
        {
            "id": 2,
            "first_name": "Jane",
            "last_name": "Smith",
            "e_mail": "jane.smith@example.com"
        }
    ]
    """
    result = await session.execute(select(Seller))
    sellers = result.scalars().all()
    return sellers


@sellers_router.get("/{seller_id}", response_model=SellerWithBooks)
async def get_seller(seller_id: int, session: DBSession, curr_user: current_user):
    """
    Получение информации о продавце по его ID.

    Эта функция возвращает данные о продавце и его книгах, если он существует в системе,
    иначе возвращает ошибку 404.

    Параметры
    ----------
    seller_id : int
        ID продавца, информацию о котором нужно получить.

    session : DBSession
        Сессия базы данных для выполнения запроса на получение продавца.

    curr_user : current_user
        Информация о текущем авторизованном пользователе (продавце).

    Возвращаемое значение
    ---------------------
    SellerWithBooks
        Данные о продавце и его книгах, если продавец найден.

    Исключения
    -----------
    HTTPException
        В случае, если продавец не найден, будет возвращен статус 404.

    Пример
    -------
    Пример успешного ответа:

    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe@example.com",
        "books": [
            {
                "id": 1,
                "title": "Book Title",
                "author": "Book Author"
            }
        ]
    }

    Пример ошибки (продавец не найден):

    HTTP 404 Not Found
    {
        "detail": "Seller not found"
    }
    """
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
    """
    Обновление данных продавца.

    Эта функция обновляет информацию о продавце (имя, фамилия, email),
    если продавец с таким ID существует.

    Параметры
    ----------
    seller_id : int
        ID продавца, данные которого необходимо обновить.

    seller_update : SellerBase
        Новые данные для обновления продавца, такие как имя, фамилия и email.

    session : DBSession
        Сессия базы данных для выполнения запроса на обновление данных продавца.

    Возвращаемое значение
    ---------------------
    SellerReturn
        Обновленные данные о продавце.

    Исключения
    -----------
    HTTPException
        В случае, если продавец с таким ID не найден, будет поднята ошибка 404.

    Пример
    -------
    Пример успешного ответа:

    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe@example.com"
    }

    Пример ошибки (продавец не найден):

    HTTP 404 Not Found
    {
        "detail": "Seller not found"
    }
    """
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
    """
    Удаление продавца.

    Эта функция удаляет продавца по его ID из базы данных. Если продавец не найден,
    будет возвращена ошибка 404.

    Параметры
    ----------
    seller_id : int
        ID продавца, которого необходимо удалить.

    session : DBSession
        Сессия базы данных для выполнения операции удаления.

    Возвращаемое значение
    ---------------------
    HTTP 204 No Content
        В случае успешного удаления продавца возвращается статус 204.

    Пример
    -------
    Пример успешного ответа: HTTP 204 No Content
    Пример ошибки: HTTP 404 Not Found
    """
    result = await session.execute(select(Seller).where(Seller.id == seller_id))
    seller = result.scalars().first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    await session.delete(seller)
    await session.commit()
    return None
