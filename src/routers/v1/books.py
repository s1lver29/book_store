from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.connection_db import async_database_session
from src.middlewares.auth import get_current_user
from src.models.books import Book
from src.models.seller import Seller
from src.schemas import IncomingBook, ReturnedAllbooks, ReturnedBook, UpdateBook

books_router = APIRouter(tags=["books"], prefix="/books")


DBSession = Annotated[AsyncSession, Depends(async_database_session)]
current_user = Annotated[Seller, Depends(get_current_user)]


@books_router.post("/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED)
async def create_book(book: IncomingBook, session: DBSession, curr_user: current_user):
    """
    Создание новой книги.

    Эта функция позволяет продавцу добавить новую книгу в систему. Книга будет
    автоматически связана с продавцом через его ID.

    Параметры
    ----------
    book : IncomingBook
        Данные о книге, которые необходимо создать, включая название, автора,
        год и количество страниц.

    session : DBSession
        Сессия базы данных для выполнения операций с книгами.

    curr_user : current_user
        Информация о текущем пользователе (продавце), который добавляет книгу.

    Возвращаемое значение
    ---------------------
    ReturnedBook
        Данные о созданной книге, включая её ID и информацию, связанную с книгой.

    Пример
    -------
    Пример успешного ответа:

    {
        "id": 1,
        "title": "Book Title",
        "author": "Book Author",
        "year": 2021,
        "pages": 350,
        "seller_id": 1
    }
    """
    new_book = Book(**book.model_dump(), seller_id=curr_user.id)

    session.add(new_book)
    await session.flush()

    return new_book


@books_router.get("/", response_model=ReturnedAllbooks)
async def get_all_books(session: DBSession):
    """
    Получение списка всех книг.

    Эта функция возвращает список всех книг, доступных в системе.

    Параметры
    ----------
    session : DBSession
        Сессия базы данных для выполнения запроса на получение книг.

    Возвращаемое значение
    ---------------------
    ReturnedAllbooks
        Словарь, содержащий список всех книг в системе.

    Пример
    -------
    Пример успешного ответа:

    {
        "books": [
            {
                "id": 1,
                "title": "Book Title",
                "author": "Book Author",
                "year": 2021,
                "pages": 350,
                "seller_id": 1
            },
            {
                "id": 2,
                "title": "Another Book",
                "author": "Another Author",
                "year": 2022,
                "pages": 420,
                "seller_id": 2
            }
        ]
    }
    """
    query = select(Book)
    result = await session.execute(query)
    books = result.scalars().all()
    return {"books": books}


@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int, session: DBSession):
    """
    Получение информации о конкретной книге по её ID.

    Эта функция возвращает данные о книге, если она существует в системе,
    иначе возвращает ошибку 404.

    Параметры
    ----------
    book_id : int
        ID книги, информацию о которой нужно получить.

    session : DBSession
        Сессия базы данных для выполнения запроса на получение книги.

    Возвращаемое значение
    ---------------------
    ReturnedBook
        Данные о книге, если она найдена в базе.

    Пример
    -------
    Пример успешного ответа:

    {
        "id": 1,
        "title": "Book Title",
        "author": "Book Author",
        "year": 2021,
        "pages": 350,
        "seller_id": 1
    }

    Пример ошибки (книга не найдена):

    HTTP 404 Not Found
    {
        "detail": "Book not found"
    }
    """
    if result := await session.get(Book, book_id):
        return result

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: DBSession):
    """
    Удаление книги.

    Эта функция удаляет книгу по её ID из базы данных. Если книга не существует,
    возвращается ошибка 404.

    Параметры
    ----------
    book_id : int
        ID книги, которую необходимо удалить.

    session : DBSession
        Сессия базы данных для выполнения операции удаления.

    Возвращаемое значение
    ---------------------
    HTTP 204 No Content
        В случае успешного удаления книги возвращается статус 204.

    Пример
    -------
    Пример успешного ответа: HTTP 204 No Content
    Пример ошибки: HTTP 404 Not Found
    """
    deleted_book = await session.get(Book, book_id)
    if deleted_book:
        await session.delete(deleted_book)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(
    book_id: int, new_book_data: UpdateBook, session: DBSession, curr_user: current_user
):
    """
    Обновление данных книги.

    Эта функция обновляет данные книги, если она существует в базе данных,
    и если продавец, пытающийся обновить книгу, является владельцем этой книги.

    Параметры
    ----------
    book_id : int
        ID книги, которую нужно обновить.

    new_book_data : UpdateBook
        Новые данные для книги, которые должны быть обновлены.

    session : DBSession
        Сессия базы данных для выполнения запроса на обновление книги.

    curr_user : current_user
        Текущий пользователь (продавец), который пытается обновить книгу.

    Возвращаемое значение
    ---------------------
    ReturnedBook
        Данные обновленной книги, если обновление прошло успешно.

    Исключения
    -----------
    HTTPException
        В случае, если книга не существует или если продавец не является владельцем книги,
        будет поднята ошибка 404 или 403.

    Пример
    -------
    Пример успешного ответа:

    {
        "id": 1,
        "title": "Updated Book Title",
        "author": "Updated Author",
        "year": 2024,
        "pages": 400,
        "seller_id": 1
    }

    Пример ошибки (книга не найдена): HTTP 404 Not Found
    Пример ошибки (неправообладание): HTTP 403 Forbidden
    """
    updated_book = await session.get(Book, book_id)
    if not updated_book:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    if updated_book.seller_id != curr_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this book",
        )

    for field, value in new_book_data.model_dump(exclude_unset=True).items():
        setattr(updated_book, field, value)

    await session.commit()
    await session.refresh(updated_book)

    return updated_book
