import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.asyncio
async def test_refresh_token_revocation(client: AsyncClient):
    # 1. Login to get tokens
    reg_data = {"email": "revoker@example.com", "password": "password123"}
    await client.post("/auth/register", json=reg_data)
    
    login_data = {"username": reg_data["email"], "password": reg_data["password"]}
    response = await client.post("/auth/login", data=login_data)
    tokens = response.json()
    refresh_token = tokens["refresh_token"]
    
    # 2. Revoke the refresh token using /revoke
    with patch("app.services.redis_service.redis_service.blacklist_token") as mock_blacklist:
        response = await client.post("/auth/revoke", json={"token": refresh_token})
        assert response.status_code == 200
        assert response.json()["detail"] == "Refresh token revoked"
        mock_blacklist.assert_called_once()
        # Extract the token and TTL from the call
        blacklisted_token = mock_blacklist.call_args[0][0]
        assert blacklisted_token == refresh_token
    
    # 3. Attempt to use the blacklisted refresh token
    with patch("app.services.redis_service.redis_service.is_token_blacklisted", return_value=True):
        response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 401
        assert response.json()["detail"] == "Refresh token has been revoked"

@pytest.mark.asyncio
async def test_logout_with_refresh_token(client: AsyncClient):
    # 1. Login
    reg_data = {"email": "logout_full@example.com", "password": "password123"}
    await client.post("/auth/register", json=reg_data)
    
    login_data = {"username": reg_data["email"], "password": reg_data["password"]}
    response = await client.post("/auth/login", data=login_data)
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    # 2. Logout with both tokens
    with patch("app.services.redis_service.redis_service.blacklist_token") as mock_blacklist:
        response = await client.post(
            "/auth/logout", 
            headers={"Authorization": f"Bearer {access_token}"},
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        assert response.json()["detail"] == "Revocation complete"
        # Should be called twice: once for access, once for refresh
        assert mock_blacklist.call_count == 2
