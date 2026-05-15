import pytest
import httpx
import asyncio
from app.main import app
from app.core.security import create_access_token

from unittest.mock import patch

# Stateful Mock for Redis Blacklist
blacklisted_tokens = set()

async def mock_is_blacklisted(token: str):
    return token in blacklisted_tokens

async def mock_blacklist(token: str, ttl: int):
    blacklisted_tokens.add(token)

@pytest.mark.asyncio
async def test_fingerprint_mismatch_auto_revocation():
    """
    Test that a token used with a different fingerprint is instantly blacklisted.
    """
    from httpx import ASGITransport
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        with patch("app.services.redis_service.redis_service.is_token_blacklisted", side_effect=mock_is_blacklisted), \
             patch("app.services.redis_service.redis_service.blacklist_token", side_effect=mock_blacklist):
            
            # 1. Create a token bound to "REAL_DEVICE"
            fingerprint = "REAL_DEVICE"
            token = create_access_token(subject="1", fingerprint=fingerprint)
            
            # 2. Attempt to use it with "HACKER_DEVICE"
            headers = {
                "Authorization": f"Bearer {token}",
                "X-Device-Fingerprint": "HACKER_DEVICE"
            }
            
            response = await ac.get("/users/me", headers=headers)
            
            # 3. Assert rejection
            assert response.status_code == 401
            assert "Identity Drift Detected" in response.json()["detail"]
            
            # 4. Assert that the token is now blacklisted even for the "REAL_DEVICE"
            real_headers = {
                "Authorization": f"Bearer {token}",
                "X-Device-Fingerprint": "REAL_DEVICE"
            }
            second_response = await ac.get("/users/me", headers=real_headers)
            assert second_response.status_code == 401
            assert "Token has been revoked" in second_response.json()["detail"]

@pytest.mark.asyncio
async def test_missing_fingerprint_on_bound_token():
    """
    Test that a bound token used without a fingerprint header is rejected.
    """
    from httpx import ASGITransport
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token = create_access_token(subject="1", fingerprint="SOME_DEVICE")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/users/me", headers=headers)
        
        assert response.status_code == 401
        assert "Device signature required" in response.json()["detail"]
