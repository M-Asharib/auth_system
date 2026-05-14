import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_auth_end_to_end_lifecycle(client: AsyncClient):
    # 1. Registration Step
    reg_data = {"email": "test@example.com", "password": "securepassword123"}
    response = await client.post("/auth/register", json=reg_data)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == reg_data["email"]
    assert "id" in user_data
    
    # 2. Authentication Step
    login_data = {"username": reg_data["email"], "password": reg_data["password"]}
    response = await client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"
    
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    # 3. Security Access Step
    response = await client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    profile = response.json()
    assert profile["email"] == reg_data["email"]
    
    # 4. Rotation Step
    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    new_tokens = response.json()
    assert new_tokens["access_token"] != access_token
    new_access_token = new_tokens["access_token"]
    
    # 5. Session Revocation Step
    response = await client.post("/auth/logout", headers={"Authorization": f"Bearer {new_access_token}"})
    assert response.status_code == 200
    assert response.json()["detail"] == "Revocation complete"
    
    # 6. Zero-Trust Post-Validation Step
    response = await client.get("/users/me", headers={"Authorization": f"Bearer {new_access_token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has been revoked"
