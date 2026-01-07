"""
Tests for car price prediction routes
"""
import pytest
from fastapi import status


def test_predict_car_price_success(test_client, auth_headers, sample_prediction_data):
    """Test successful car price prediction"""
    response = test_client.post(
        "/predict",
        json=sample_prediction_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "prediction" in data
    assert isinstance(data["prediction"], (int, float))
    assert data["prediction"] > 0


def test_predict_unauthorized(test_client, sample_prediction_data):
    """Test prediction without authentication"""
    response = test_client.post(
        "/predict",
        json=sample_prediction_data
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_predict_missing_required_fields(test_client, auth_headers):
    """Test prediction with missing required car fields"""
    incomplete_data = {
        "company": "Maruti",
        "year": 2015
        # Missing other required fields
    }
    
    response = test_client.post(
        "/predict",
        json=incomplete_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_predict_invalid_year(test_client, auth_headers, sample_prediction_data):
    """Test prediction with invalid year (future year)"""
    invalid_data = sample_prediction_data.copy()
    invalid_data["year"] = 2050
    
    response = test_client.post(
        "/predict",
        json=invalid_data,
        headers=auth_headers
    )
    
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


def test_predict_negative_km_driven(test_client, auth_headers, sample_prediction_data):
    """Test prediction with negative kilometers"""
    invalid_data = sample_prediction_data.copy()
    invalid_data["km_driven"] = -5000
    
    response = test_client.post(
        "/predict",
        json=invalid_data,
        headers=auth_headers
    )
    
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


def test_predict_invalid_fuel_type(test_client, auth_headers, sample_prediction_data):
    """Test prediction with invalid fuel type"""
    invalid_data = sample_prediction_data.copy()
    invalid_data["fuel"] = "Nuclear"
    
    response = test_client.post(
        "/predict",
        json=invalid_data,
        headers=auth_headers
    )
    
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


def test_predict_different_car_brands(test_client, auth_headers):
    """Test predictions for different car brands"""
    brands = ["Maruti", "Hyundai", "Honda", "Toyota", "Ford"]
    
    for brand in brands:
        car_data = {
            "company": brand,
            "year": 2018,
            "owner": "First",
            "fuel": "Petrol",
            "seller_type": "Dealer",
            "transmission": "Manual",
            "km_driven": 30000,
            "mileage_mpg": 55,
            "engine_cc": 1200,
            "max_power_bhp": 80,
            "torque_nm": 200,
            "seats": 5
        }
        
        response = test_client.post(
            "/predict",
            json=car_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK


def test_predict_batch_cars(test_client, auth_headers, sample_car_data_list):
    """Test batch prediction for multiple cars"""
    response = test_client.post(
        "/predict/batch",
        json={"cars": sample_car_data_list},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) == len(sample_car_data_list)


def test_predict_empty_body(test_client, auth_headers):
    """Test prediction with empty request body"""
    response = test_client.post(
        "/predict",
        json={},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_predict_high_mileage_car(test_client, auth_headers, sample_prediction_data):
    """Test prediction for high mileage car"""
    high_mileage_data = sample_prediction_data.copy()
    high_mileage_data["km_driven"] = 500000  # Very high mileage
    
    response = test_client.post(
        "/predict",
        json=high_mileage_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # High mileage should result in lower price
    assert data["prediction"] > 0


def test_predict_new_car(test_client, auth_headers):
    """Test prediction for nearly new car"""
    new_car_data = {
        "company": "Honda",
        "year": 2023,
        "owner": "First",
        "fuel": "Petrol",
        "seller_type": "Dealer",
        "transmission": "Automatic",
        "km_driven": 5000,
        "mileage_mpg": 70,
        "engine_cc": 1500,
        "max_power_bhp": 110,
        "torque_nm": 250,
        "seats": 5
    }
    
    response = test_client.post(
        "/predict",
        json=new_car_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK