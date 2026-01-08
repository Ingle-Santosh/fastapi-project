import joblib
import pandas as pd
import logging
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, List
from app.core.config import settings
from app.cache.redis_cache import get_cached_prediction, set_cached_prediction
from app.core.custom_exceptions import ModelNotLoadedException, PredictionException

logger = logging.getLogger(__name__)

# Global model variable
_model = None

def load_model():
    """
    Load the ML model from disk
    Raises ModelNotLoadedException if model file not found
    """
    global _model
    
    if _model is not None:
        return _model
    
    model_path = Path(settings.MODEL_PATH)
    
    if not model_path.exists():
        logger.error(f"Model file not found at: {settings.MODEL_PATH}")
        raise ModelNotLoadedException(f"Model file not found: {settings.MODEL_PATH}")
    
    try:
        _model = joblib.load(settings.MODEL_PATH)
        logger.info(f"✅ Model loaded successfully from {settings.MODEL_PATH}")
        return _model
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise ModelNotLoadedException(f"Failed to load model: {str(e)}")
    
def get_model():
    """
    Get the loaded model instance
    """
    global _model
    if _model is None:
        _model = load_model()
    return _model

def generate_cache_key(data: dict) -> str:
    """
    Generate a consistent cache key from input data
    Uses hash for better key management
    """
    # Sort keys for consistency
    sorted_data = {k: data[k] for k in sorted(data.keys())}
    data_str = json.dumps(sorted_data, sort_keys=True)
    
    # Generate hash for clean cache key
    hash_key = hashlib.md5(data_str.encode()).hexdigest()
    return f"prediction:{hash_key}"

def validate_input_data(data: dict) -> None:
    """
    Validate input data before prediction
    """
    required_fields = [
        'company', 'year', 'owner', 'fuel', 'seller_type',
        'transmission', 'km_driven', 'mileage_mpg', 'engine_cc',
        'max_power_bhp', 'torque_nm', 'seats'
    ]
    
    # Check for missing fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Validate numeric fields
    if data['year'] < 1900 or data['year'] > 2030:
        raise ValueError(f"Invalid year: {data['year']}. Must be between 1900 and 2030")
    
    if data['km_driven'] < 0:
        raise ValueError(f"Invalid km_driven: {data['km_driven']}. Cannot be negative")
    
    if data['seats'] < 2 or data['seats'] > 10:
        raise ValueError(f"Invalid seats: {data['seats']}. Must be between 2 and 10")

def predict_car_price(data: dict) -> float:
    """
    Predict car price using the ML model
    
    Args:
        data: Dictionary containing car features
        
    Returns:
        Predicted price as float
        
    Raises:
        PredictionException: If prediction fails
        ValueError: If input validation fails
    """
    try:
        # Validate input
        validate_input_data(data)
        
        # Generate cache key
        cache_key = generate_cache_key(data)
        
        # Check cache
        cached = get_cached_prediction(cache_key)
        if cached is not None:
            logger.info(f"Cache hit for key: {cache_key}")
            return float(cached)
        
        logger.info(f"Cache miss for key: {cache_key}")
        
        # Get model
        model = get_model()
        
        # Prepare input data
        input_data = pd.DataFrame([data])
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        prediction = float(prediction)
        
        # Cache the result
        set_cached_prediction(cache_key, prediction)
        
        logger.info(f"Prediction successful: {prediction:.2f}")
        return prediction
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise  # Re-raise ValueError for proper handling
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise PredictionException(f"Prediction failed: {str(e)}")
    

def batch_predict(data_list: List[dict]) -> List[float]:
    """
    Predict prices for multiple cars
    
    Args:
        data_list: List of dictionaries containing car features
        
    Returns:
        List of predicted prices
    """
    predictions = []
    
    for data in data_list:
        try:
            prediction = predict_car_price(data)
            predictions.append(prediction)
        except Exception as e:
            logger.error(f"Batch prediction error for data {data}: {str(e)}")
            predictions.append(None)
    
    return predictions

def get_model_info() -> Dict:
    """
    Get information about the loaded model
    """
    try:
        model = get_model()
        return {
            "model_type": type(model).__name__,
            "model_path": settings.MODEL_PATH,
            "version": settings.MODEL_VERSION,
            "is_loaded": _model is not None
        }
    except Exception as e:
        return {
            "error": str(e),
            "is_loaded": False
        }


# Load model on module import
try:
    load_model()
except Exception as e:
    logger.warning(f"Model not loaded on startup: {str(e)}")