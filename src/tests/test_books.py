import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.books import Book
from src.models.seller import Seller

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session):
    user_data = {
        "first_name": "First",
        "last_name": "Last",
        "e_mail": "test@example.com",
        "password": pwd_context.hash("testpassword"),
    }

    existing_user = await db_session.execute(
        select(Seller).filter(Seller.e_mail == user_data["e_mail"])
    )
    existing_user = existing_user.scalars().first()

    if not existing_user:
        user = Seller(**user_data)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user
    return existing_user


@pytest.mark.asyncio
async def test_login_for_access_token(async_client: AsyncClient, test_user: Seller):
    login_data = {"username": test_user.e_mail, "password": "testpassword"}

    response = await async_client.post("/api/v1/token", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()


@pytest.mark.asyncio
async def test_create_book(async_client: AsyncClient, db_session, test_user: Seller):
    book_data = {"title": "Test Book", "author": "Test Author", "year": 2020, "pages": 100}

    login_data = {"username": test_user.e_mail, "password": "testpassword"}
    login_response = await async_client.post("/api/v1/token", data=login_data)
    token = login_response.json()["access_token"]

    response = await async_client.post(
        "/api/v1/books/", json=book_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.json()["title"] == book_data["title"]
    assert response.json()["author"] == book_data["author"]
    assert response.json()["year"] == book_data["year"]
    assert response.json()["pages"] == book_data["pages"]


@pytest.mark.asyncio
async def test_get_all_books(async_client: AsyncClient, db_session: AsyncSession):
    response = await async_client.get("/api/v1/books/")
    assert response.status_code == 200
    assert "books" in response.json()


@pytest.mark.asyncio
async def test_get_book(async_client: AsyncClient, db_session: AsyncSession):
    book = Book(title="Sample Book", author="Sample Author", year=2020, pages=100, seller_id=1)
    db_session.add(book)
    await db_session.commit()

    await db_session.refresh(book)
    book_id = book.id

    response = await async_client.get(f"/api/v1/books/{book_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["title"] == book.title
    assert data["author"] == book.author
    assert data["year"] == book.year
    assert data["pages"] == book.pages


@pytest.mark.asyncio
async def test_update_book(async_client: AsyncClient, db_session: AsyncSession, test_user: Seller):
    login_data = {"username": test_user.e_mail, "password": "testpassword"}
    login_response = await async_client.post("/api/v1/token", data=login_data)
    token = login_response.json()["access_token"]

    book = Book(
        title="Old Title", author="Old Author", year=2020, pages=100, seller_id=test_user.id
    )
    db_session.add(book)
    await db_session.commit()

    await db_session.refresh(book)
    book_id = book.id

    update_data = {"title": "New Title", "year": 2024}
    response = await async_client.put(
        f"/api/v1/books/{book_id}", json=update_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "New Title"
    assert data["year"] == 2024


@pytest.mark.asyncio
async def test_delete_book(async_client: AsyncClient, db_session: AsyncSession):
    book = Book(title="Del Book", author="Del Author", year=2020, pages=100, seller_id=1)
    db_session.add(book)
    await db_session.commit()

    await db_session.refresh(book)
    book_id = book.id

    response = await async_client.delete(f"/api/v1/books/{book_id}")
    assert response.status_code == 204

    await db_session.commit()

    response = await async_client.delete(f"/api/v1/books/{book_id}")
    assert response.status_code == 404

    response = await async_client.get(f"/api/v1/books/{book_id}")
    assert response.status_code == 404
