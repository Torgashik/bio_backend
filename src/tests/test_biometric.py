import pytest
from datetime import datetime
from fastapi import status

from app.models.models import BiometricDataType, Organization, User, UserRole, BiometricData
from app.utils.auth import create_access_token

API_PREFIX = "/api/v1"

def test_create_biometric_data(client, test_user, test_organization, db):
    # Ensure both user and organization are attached to session
    db.add(test_organization)
    db.add(test_user)
    db.commit()
    db.refresh(test_organization)
    db.refresh(test_user)
    
    # Store IDs before making request
    user_id = test_user.id
    org_id = test_organization.id
    
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.post(
        f"{API_PREFIX}/biometric/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "data_type": BiometricDataType.FINGERPRINT,
            "value": 123.45,
            "timestamp": datetime.utcnow().isoformat(),
            "data_metadata": {"quality": "high"}
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["data_type"] == BiometricDataType.FINGERPRINT
    assert data["value"] == 123.45
    assert data["user_id"] == user_id
    assert data["organization_id"] == org_id

def test_get_biometric_data(client, test_user, test_biometric_data):
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.get(
        f"{API_PREFIX}/biometric/{test_biometric_data.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_biometric_data.id
    assert data["data_type"] == BiometricDataType.FINGERPRINT
    assert data["value"] == 123.45

def test_update_biometric_data(client, test_user, test_biometric_data):
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.put(
        f"{API_PREFIX}/biometric/{test_biometric_data.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "value": 234.56,
            "data_metadata": {"quality": "medium"}
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["value"] == 234.56
    assert data["data_metadata"] == {"quality": "medium"}

def test_delete_biometric_data(client, test_user, test_biometric_data):
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.delete(
        f"{API_PREFIX}/biometric/{test_biometric_data.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Biometric data deleted successfully"

def test_list_biometric_data(client, test_user, test_biometric_data):
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.get(
        f"{API_PREFIX}/biometric/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_biometric_data.id

def test_get_analytics(client, test_user, test_biometric_data):
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.get(
        f"{API_PREFIX}/biometric/analytics/",
        params={"data_type": BiometricDataType.FINGERPRINT.value},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["data_type"] == BiometricDataType.FINGERPRINT.value
    assert data["count"] == 1
    assert data["average"] == 123.45
    assert data["min"] == 123.45
    assert data["max"] == 123.45
    assert "organization_id" in data["metadata"]
    assert "analysis_timestamp" in data["metadata"]

def test_create_biometric_data_no_organization(client, test_user):
    # Remove organization from user
    test_user.organization_id = None
    
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.post(
        f"{API_PREFIX}/biometric/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "data_type": BiometricDataType.FINGERPRINT,
            "value": 123.45,
            "timestamp": datetime.utcnow().isoformat(),
            "data_metadata": {"quality": "high"}
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "User must be associated with an organization"

def test_get_biometric_data_wrong_organization(client, test_user, test_organization, db):
    # Create a new organization
    new_org = Organization(name="Wrong Organization")
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    # Create biometric data for the new organization
    biometric_data = BiometricData(
        user_id=test_user.id,
        organization_id=new_org.id,
        data_type=BiometricDataType.FINGERPRINT,
        value=123.45,
        timestamp=datetime.utcnow(),
        data_metadata={"quality": "high"}
    )
    db.add(biometric_data)
    db.commit()
    db.refresh(biometric_data)
    
    # Try to access the data with the original user's token
    token = create_access_token({"sub": test_user.email, "role": test_user.role})
    response = client.get(
        f"{API_PREFIX}/biometric/{biometric_data.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Create a new organization and user
    new_org = Organization(name="New Org", contact_email="new@org.com")
    db.add(new_org)
    db.commit()
    
    new_user = User(
        email="new@example.com",
        hashed_password="hashed_password",
        role=UserRole.USER,
        organization_id=new_org.id
    )
    db.add(new_user)
    db.commit()
    
    token = create_access_token({"sub": new_user.email, "role": new_user.role})
    response = client.get(
        f"{API_PREFIX}/biometric/{biometric_data.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized to access this data" 