import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_seller(async_client: AsyncClient):
    seller_data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe@example.com",
        "password": "password123",
    }
    response = await async_client.post("/api/v1/sellers/", json=seller_data)
    assert response.status_code == 201
    data = response.json()

    assert data["first_name"] == seller_data["first_name"]
    assert data["last_name"] == seller_data["last_name"]
    assert data["e_mail"] == seller_data["e_mail"]


@pytest.mark.asyncio
async def test_get_all_sellers(async_client: AsyncClient):
    response = await async_client.get("/api/v1/sellers/")
    assert response.status_code == 200
    sellers = response.json()
    assert isinstance(sellers, list)
    assert len(sellers) > 0


@pytest.mark.asyncio
async def test_get_seller_by_id(async_client: AsyncClient, db_session: AsyncSession):
    seller_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "e_mail": "jane.smith@example.com",
        "password": "password123",
    }
    response = await async_client.post("/api/v1/sellers/", json=seller_data)
    seller = response.json()

    seller_id = seller["id"]

    login_data = {"username": "jane.smith@example.com", "password": "password123"}
    login_response = await async_client.post("/api/v1/token", data=login_data)
    token = login_response.json()["access_token"]

    response = await async_client.get(
        f"/api/v1/sellers/{seller_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == seller_id


@pytest.mark.asyncio
async def test_get_seller_by_id_not_auth(async_client: AsyncClient):
    response = await async_client.get("/api/v1/sellers/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_seller(async_client: AsyncClient, db_session: AsyncSession):
    seller_data = {
        "first_name": "Alice",
        "last_name": "Wonder",
        "e_mail": "alice.wonder@example.com",
        "password": "password123",
    }
    response = await async_client.post("/api/v1/sellers/", json=seller_data)
    seller = response.json()

    seller_id = seller["id"]
    update_data = {
        "first_name": "Alice Updated",
        "last_name": "Wonder Updated",
        "e_mail": "alice.updated@example.com",
    }

    response = await async_client.put(f"/api/v1/sellers/{seller_id}", json=update_data)
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["first_name"] == "Alice Updated"
    assert updated_data["e_mail"] == "alice.updated@example.com"


@pytest.mark.asyncio
async def test_update_seller_not_found(async_client: AsyncClient):
    update_data = {"first_name": "Updated", "last_name": "Name", "e_mail": "updated@example.com"}
    response = await async_client.put("/api/v1/sellers/9999999", json=update_data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_seller(async_client: AsyncClient, db_session: AsyncSession):
    seller_data = {
        "first_name": "Bob",
        "last_name": "Marley",
        "e_mail": "bob.marley@example.com",
        "password": "password123",
    }
    response = await async_client.post("/api/v1/sellers/", json=seller_data)
    seller = response.json()

    seller_id = seller["id"]

    response = await async_client.delete(f"/api/v1/sellers/{seller_id}")
    assert response.status_code == 204

    db_session.commit()

    response = await async_client.delete(f"/api/v1/sellers/{seller_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_seller_not_found(async_client: AsyncClient):
    response = await async_client.delete("/api/v1/sellers/9999999")
    assert response.status_code == 404
