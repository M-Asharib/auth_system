import pytest
from httpx import AsyncClient
from sqlalchemy import update
from app.models.user import User
from tests.conftest import TestingSessionLocal

@pytest.mark.asyncio
async def test_policy_management(client: AsyncClient):
    # Setup: Create a regular user and an admin user
    reg_data = {"email": "user@example.com", "password": "password123"}
    await client.post("/auth/register", json=reg_data)
    
    admin_data = {"email": "admin@example.com", "password": "adminpassword"}
    res_admin_reg = await client.post("/auth/register", json=admin_data)
    admin_id = res_admin_reg.json()["id"]

    # Manually promote to superuser in test DB
    async with TestingSessionLocal() as session:
        await session.execute(update(User).where(User.id == admin_id).values(is_superuser=True))
        await session.commit()

    # Login as admin
    res_login = await client.post("/auth/login", data={"username": admin_data["email"], "password": admin_data["password"]})
    admin_token = res_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Test Per-User TTL Override
    target_user_id = 1 # The first user created
    res_policy = await client.patch(
        f"/users/{target_user_id}/policy", 
        json={"expires_minutes": 5},
        headers=admin_headers
    )
    assert res_policy.status_code == 200
    assert res_policy.json()["access_token_expires_minutes"] == 5

    # 2. Test Bulk Policy Update
    res_bulk = await client.post(
        "/users/policy/bulk", 
        json={"expires_minutes": 30},
        headers=admin_headers
    )
    assert res_bulk.status_code == 200
    assert "30m" in res_bulk.json()["detail"]

    # Verify bulk change in DB
    res_users = await client.get("/users/", headers=admin_headers)
    users = res_users.json()
    for user in users:
        assert user["access_token_expires_minutes"] == 30
