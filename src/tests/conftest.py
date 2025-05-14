import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from passlib.context import CryptContext
from datetime import datetime
from typing import Dict, Any, List
from tests.dashboard import generate_test_dashboard

from app.main import app
from app.database.database import Base, get_db
from app.models.models import User, UserRole, Organization, BiometricDataType, BiometricData
from app.utils.auth import create_access_token, get_password_hash

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Store test results
test_results: Dict[str, Any] = {
    "tests": [],
    "start_time": None,
    "end_time": None
}

@pytest.fixture(scope="function")
def db():
    # Create tables in test database
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app=app)

@pytest.fixture(scope="function")
def test_organization(db):
    organization = Organization(
        name="Test Organization",
        contact_email="test@org.com"
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization

@pytest.fixture(scope="function")
def test_user(db, test_organization):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        role=UserRole.USER,
        organization_id=test_organization.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin(db, test_organization):
    admin = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        role=UserRole.ADMIN,
        organization_id=test_organization.id
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def test_org_user(db, test_organization):
    org_user = User(
        email="org@example.com",
        hashed_password=get_password_hash("orgpassword"),
        role=UserRole.ORGANIZATION,
        organization_id=test_organization.id
    )
    db.add(org_user)
    db.commit()
    db.refresh(org_user)
    return org_user

@pytest.fixture(scope="function")
def test_biometric_data(db, test_user, test_organization):
    data = BiometricData(
        user_id=test_user.id,
        organization_id=test_organization.id,
        data_type=BiometricDataType.FINGERPRINT,
        value=123.45,
        timestamp=datetime.utcnow(),
        data_metadata={"quality": "high"}
    )
    db.add(data)
    db.commit()
    db.refresh(data)
    return data

@pytest.fixture(scope="function")
def test_user_token(test_user):
    return create_access_token({"sub": test_user.email})

@pytest.fixture(scope="function")
def test_organization_token(test_org_user):
    return create_access_token({"sub": test_org_user.email})

@pytest.fixture(scope="function")
def test_admin_token(test_admin):
    return create_access_token({"sub": test_admin.email})

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Initialize test results at the start of the test session."""
    test_results["start_time"] = datetime.now()

@pytest.hookimpl(tryfirst=True)
def pytest_unconfigure(config):
    """Generate dashboard at the end of the test session."""
    test_results["end_time"] = datetime.now()
    dashboard_path = generate_test_dashboard(test_results)
    print(f"\nTest dashboard generated: {dashboard_path}")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Collect test results after each test."""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":  # Only process the actual test call, not setup/teardown
        test_info = {
            "name": item.name,
            "status": "passed" if report.passed else "failed",
            "duration": report.duration,
            "error": str(report.longrepr) if report.failed else None,
            "warnings": []  # Initialize empty warnings list
        }
        
        # Add warnings if they exist
        if hasattr(report, "warnings"):
            test_info["warnings"] = [str(warning.message) for warning in report.warnings]
        
        test_results["tests"].append(test_info) 