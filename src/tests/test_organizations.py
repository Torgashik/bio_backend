import pytest
from fastapi import status

from app.models.models import UserRole
from app.utils.auth import create_access_token

def test_create_organization(client, test_admin):
    token = create_access_token({"sub": test_admin.email, "role": test_admin.role})
    response = client.post(
        "/api/v1/organizations/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "New Organization",
            "contact_email": "new@org.com"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "New Organization"
    assert data["contact_email"] == "new@org.com"

def test_get_organization(client, test_admin, test_organization):
    token = create_access_token({"sub": test_admin.email, "role": test_admin.role})
    response = client.get(
        f"/api/v1/organizations/{test_organization.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_organization.id
    assert data["name"] == test_organization.name
    assert data["contact_email"] == test_organization.contact_email

def test_update_organization(client, test_admin, test_organization):
    token = create_access_token({"sub": test_admin.email, "role": test_admin.role})
    response = client.put(
        f"/api/v1/organizations/{test_organization.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Organization",
            "contact_email": "updated@org.com"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Organization"
    assert data["contact_email"] == "updated@org.com"

def test_delete_organization(client, test_admin, test_organization):
    token = create_access_token({"sub": test_admin.email, "role": test_admin.role})
    response = client.delete(
        f"/api/v1/organizations/{test_organization.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Organization deleted successfully"

def test_list_organizations(client, test_admin, test_organization):
    token = create_access_token({"sub": test_admin.email, "role": test_admin.role})
    response = client.get(
        "/api/v1/organizations/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_organization.id

def test_create_organization_unauthorized(client, test_user):
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.post(
        "/api/v1/organizations/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "New Organization",
            "contact_email": "new@org.com"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not enough permissions"

def test_get_organization_unauthorized(client, test_user, test_organization):
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.get(
        f"/api/v1/organizations/{test_organization.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not enough permissions"

def test_update_organization_unauthorized(client, test_user, test_organization):
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.put(
        f"/api/v1/organizations/{test_organization.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Organization",
            "contact_email": "updated@org.com"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not enough permissions"

def test_delete_organization_unauthorized(client, test_user, test_organization):
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.delete(
        f"/api/v1/organizations/{test_organization.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not enough permissions"

def test_list_organizations_unauthorized(client, test_user):
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.get(
        "/api/v1/organizations/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not enough permissions" 