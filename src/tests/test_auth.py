import pytest
from fastapi import status
from app.models.models import UserRole
from app.utils.auth import create_access_token, get_password_hash

API_PREFIX = "/api/v1"

def test_register_user(client, test_organization, db):
    # Ensure organization is attached to session and refreshed
    db.add(test_organization)
    db.commit()
    db.refresh(test_organization)
    
    # Store organization ID before making request
    org_id = test_organization.id
    
    response = client.post(
        f"{API_PREFIX}/register",
        json={
            "email": "new@example.com",
            "password": "testpassword",
            "organization_id": org_id
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["organization_id"] == org_id

def test_register_duplicate_email(client, test_user):
    response = client.post(
        f"{API_PREFIX}/register",
        json={
            "email": test_user.email,
            "password": "newpassword",
            "organization_id": test_user.organization_id
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client, test_user):
    response = client.post(
        f"{API_PREFIX}/token",
        data={
            "username": test_user.email,
            "password": "testpassword"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    response = client.post(
        f"{API_PREFIX}/token",
        data={
            "username": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"

def test_get_current_user(client, test_user):
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.get(
        f"{API_PREFIX}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["role"] == test_user.role
    assert data["organization_id"] == test_user.organization_id

def test_get_current_user_no_token(client):
    response = client.get(f"{API_PREFIX}/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"

def test_get_current_user_invalid_token(client):
    response = client.get(
        f"{API_PREFIX}/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Could not validate credentials"

def test_get_current_user_wrong_role(client, test_user):
    # Create token with wrong role
    token = create_access_token({"sub": test_user.email, "role": UserRole.ADMIN})
    response = client.get(
        f"{API_PREFIX}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Could not validate credentials" 