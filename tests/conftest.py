"""
Pytest configuration and shared fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_prediction_data():
    """Sample car data for prediction tests"""
    return {
        "company": "Maruti",
        "year": 2015,
        "owner": "Second",
        "fuel": "Petrol",
        "seller_type": "Individual",
        "transmission": "Automatic",
        "km_driven": 200000,
        "mileage_mpg": 55,
        "engine_cc": 1250,
        "max_power_bhp": 80,
        "torque_nm": 200,
        "seats": 5
    }

@pytest.fixture
def invalid_car_data():
    """Invalid car data for error testing"""
    return {
        "company": "Maruti",
        "year": 2050,  # Future year
        "owner": "Fifth",  # Invalid owner type
        "fuel": "Electric",  # Invalid fuel type if not supported
        "km_driven": -1000,  # Negative value
        "seats": 0  # Invalid seats
    }

@pytest.fixture
def mock_jwt_token():
    """Generate mock JWT token for testing"""
    return "test.jwt.token"


@pytest.fixture
def auth_headers(mock_jwt_token):
    """Headers with authentication token"""
    return {
        "Authorization": f"Bearer {mock_jwt_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for auth tests"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }