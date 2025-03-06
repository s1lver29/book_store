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
    new_book = Book(**book.model_dump(), seller_id=curr_user.id)

    session.add(new_book)
    await session.flush()

    return new_book


@books_router.get("/", response_model=ReturnedAllbooks)
async def get_all_books(session: DBSession):
    query = select(Book)
    result = await session.execute(query)
    books = result.scalars().all()
    return {"books": books}


@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int, session: DBSession):
    if result := await session.get(Book, book_id):
        return result

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления книги
@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: DBSession):
    deleted_book = await session.get(Book, book_id)
    if deleted_book:
        await session.delete(deleted_book)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(
    book_id: int, new_book_data: UpdateBook, session: DBSession, curr_user: current_user
):
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
