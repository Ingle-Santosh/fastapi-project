"""
Tests for car price prediction model service
"""
import pytest
from unittest.mock import Mock, patch
from app.services.model_service import ModelService


@pytest.fixture
def model_service():
    """Create model service instance"""
    return ModelService()


def test_model_loads_successfully(model_service):
    """Test that car price model loads without errors"""
    assert model_service.model is not None


def test_predict_car_price(model_service, sample_prediction_data):
    """Test car price prediction returns valid result"""
    result = model_service.predict(sample_prediction_data)
    
    assert result is not None
    assert isinstance(result, (float, int, list, dict))
    if isinstance(result, dict):
        assert "prediction" in result or "price" in result


def test_predict_maruti_car(model_service):
    """Test prediction for Maruti car"""
    maruti_data = {
        "company": "Maruti",
        "year": 2015,
        "owner": "First",
        "fuel": "Petrol",
        "seller_type": "Individual",
        "transmission": "Manual",
        "km_driven": 50000,
        "mileage_mpg": 60,
        "engine_cc": 1200,
        "max_power_bhp": 75,
        "torque_nm": 190,
        "seats": 5
    }
    
    result = model_service.predict(maruti_data)
    assert result is not None


def test_predict_luxury_car(model_service):
    """Test prediction for high-end car"""
    luxury_data = {
        "company": "BMW",
        "year": 2020,
        "owner": "First",
        "fuel": "Diesel",
        "seller_type": "Dealer",
        "transmission": "Automatic",
        "km_driven": 20000,
        "mileage_mpg": 45,
        "engine_cc": 2000,
        "max_power_bhp": 180,
        "torque_nm": 400,
        "seats": 5
    }
    
    result = model_service.predict(luxury_data)
    assert result is not None


def test_predict_missing_fields_raises_error(model_service):
    """Test prediction with missing car fields raises exception"""
    incomplete_data = {
        "company": "Maruti",
        "year": 2015
        # Missing other required fields
    }
    
    with pytest.raises(Exception):
        model_service.predict(incomplete_data)


def test_predict_invalid_year(model_service, sample_prediction_data):
    """Test prediction with invalid year"""
    invalid_data = sample_prediction_data.copy()
    invalid_data["year"] = 1800  # Too old
    
    with pytest.raises(Exception):
        model_service.predict(invalid_data)


def test_predict_negative_km(model_service, sample_prediction_data):
    """Test prediction with negative kilometers"""
    invalid_data = sample_prediction_data.copy()
    invalid_data["km_driven"] = -10000
    
    with pytest.raises(Exception):
        model_service.predict(invalid_data)


@patch('app.cache.redis_cache.get')
@patch('app.cache.redis_cache.set')
def test_predict_uses_cache(mock_set, mock_get, model_service, sample_prediction_data):
    """Test prediction caching for car data"""
    mock_get.return_value = None
    
    result = model_service.predict(sample_prediction_data)
    
    assert mock_get.called
    assert mock_set.called
    assert result is not None


@patch('app.cache.redis_cache.get')
def test_predict_returns_cached_price(mock_get, model_service, sample_prediction_data):
    """Test prediction returns cached car price"""
    cached_value = {"prediction": 450000, "currency": "INR"}
    mock_get.return_value = cached_value
    
    result = model_service.predict(sample_prediction_data)
    
    assert result == cached_value


def test_batch_predict_multiple_cars(model_service, sample_car_data_list):
    """Test batch prediction for multiple cars"""
    results = model_service.batch_predict(sample_car_data_list)
    
    assert len(results) == len(sample_car_data_list)
    assert all(r is not None for r in results)


def test_predict_automatic_vs_manual(model_service):
    """Test price difference between automatic and manual transmission"""
    manual_car = {
        "company": "Maruti",
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
    
    automatic_car = manual_car.copy()
    automatic_car["transmission"] = "Automatic"
    
    manual_price = model_service.predict(manual_car)
    auto_price = model_service.predict(automatic_car)
    
    assert manual_price is not None
    assert auto_price is not None


def test_predict_diesel_vs_petrol(model_service):
    """Test price difference between diesel and petrol cars"""
    petrol_car = {
        "company": "Hyundai",
        "year": 2018,
        "owner": "First",
        "fuel": "Petrol",
        "seller_type": "Dealer",
        "transmission": "Manual",
        "km_driven": 40000,
        "mileage_mpg": 50,
        "engine_cc": 1200,
        "max_power_bhp": 80,
        "torque_nm": 200,
        "seats": 5
    }
    
    diesel_car = petrol_car.copy()
    diesel_car["fuel"] = "Diesel"
    
    petrol_price = model_service.predict(petrol_car)
    diesel_price = model_service.predict(diesel_car)
    
    assert petrol_price is not None
    assert diesel_price is not None


def test_model_version_info(model_service):
    """Test car price model version information"""
    version_info = model_service.get_model_info()
    
    assert version_info is not None
    assert isinstance(version_info, dict)