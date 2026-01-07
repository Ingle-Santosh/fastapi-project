"""
Tests for authentication routes
"""
import pytest
from fastapi import status


def test_login_success(test_client, sample_user_data):
    """Test successful login"""
    login_data = {
        "username": sample_user_data["username"],
        "password": sample_user_data["password"]
    }
    
    response = test_client.post("/login", json=login_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(test_client):
    """Test login with wrong credentials"""
    login_data = {
        "username": "wronguser",
        "password": "wrongpass"
    }
    
    response = test_client.post("/login", json=login_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_missing_username(test_client):
    """Test login without username"""
    login_data = {"password": "testpass"}
    
    response = test_client.post("/login", json=login_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_missing_password(test_client):
    """Test login without password"""
    login_data = {"username": "testuser"}
    
    response = test_client.post("/login", json=login_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_success(test_client):
    """Test successful user registration"""
    register_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepass123"
    }
    
    response = test_client.post("/register", json=register_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data or "username" in data


def test_register_duplicate_username(test_client, sample_user_data):
    """Test registration with existing username"""
    response = test_client.post("/register", json=sample_user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_register_invalid_email(test_client):
    """Test registration with invalid email"""
    register_data = {
        "username": "testuser",
        "email": "invalid-email",
        "password": "pass123"
    }
    
    response = test_client.post("/register", json=register_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_weak_password(test_client):
    """Test registration with weak password"""
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123"
    }
    
    response = test_client.post("/register", json=register_data)
    
    # Should fail validation if password requirements exist
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]