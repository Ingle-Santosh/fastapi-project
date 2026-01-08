from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.dependencies import get_api_key, get_current_user
from app.core.database import get_db
from app.services.model_service import predict_car_price, batch_predict, get_model_info
from app.database.models import Prediction, User

router = APIRouter()

class CarFeatures(BaseModel):
    company: str
    year: int
    owner: str
    fuel: str
    seller_type: str
    transmission: str
    km_driven: float
    mileage_mpg: float
    engine_cc: float
    max_power_bhp: float
    torque_nm: float
    seats: float

class BatchPredictionRequest(BaseModel):
    cars: list[CarFeatures]


@router.post('/predict')
def predict_price(
    car: CarFeatures, 
    user: User = Depends(get_current_user),
    _: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Predict car price and save to database
    Requires: Authorization header with Bearer token and X-API-Key header
    """
    # Make prediction
    prediction = predict_car_price(car.model_dump())
    
    # Save prediction to database
    db_prediction = Prediction(
        user_id=user.id,
        company=car.company,
        year=car.year,
        owner=car.owner,
        fuel=car.fuel,
        seller_type=car.seller_type,
        transmission=car.transmission,
        km_driven=int(car.km_driven),
        mileage_mpg=car.mileage_mpg,
        engine_cc=int(car.engine_cc),
        max_power_bhp=car.max_power_bhp,
        torque_nm=car.torque_nm,
        seats=int(car.seats),
        predicted_price=prediction,
        model_version="1.0.0"
    )
    
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return {
        'predicted_price': f'{prediction:,.2f}',
        'prediction_id': db_prediction.id,
        'user': user.username,
        'saved_at': db_prediction.created_at.isoformat()
    }


@router.post('/predict/batch')
def predict_batch(
    request: BatchPredictionRequest,
    user: User = Depends(get_current_user),
    _: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Predict prices for multiple cars
    Requires: Authorization header with Bearer token and X-API-Key header
    """
    car_data_list = [car.model_dump() for car in request.cars]
    predictions = batch_predict(car_data_list)
    
    # Save all predictions
    saved_ids = []
    for car, prediction in zip(request.cars, predictions):
        if prediction is not None:
            db_prediction = Prediction(
                user_id=user.id,
                company=car.company,
                year=car.year,
                owner=car.owner,
                fuel=car.fuel,
                seller_type=car.seller_type,
                transmission=car.transmission,
                km_driven=int(car.km_driven),
                mileage_mpg=car.mileage_mpg,
                engine_cc=int(car.engine_cc),
                max_power_bhp=car.max_power_bhp,
                torque_nm=car.torque_nm,
                seats=int(car.seats),
                predicted_price=prediction,
                model_version="1.0.0"
            )
            db.add(db_prediction)
            db.commit()
            db.refresh(db_prediction)
            saved_ids.append(db_prediction.id)
    
    return {
        'total': len(predictions),
        'predictions': [f'{p:,.2f}' if p else 'Failed' for p in predictions],
        'saved_ids': saved_ids,
        'user': user.username
    }


@router.get('/predictions/history')
def get_prediction_history(
    user: User = Depends(get_current_user),
    _: str = Depends(get_api_key),
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0
):
    """
    Get user's prediction history with pagination
    Requires: Authorization header with Bearer token and X-API-Key header
    """
    predictions = db.query(Prediction)\
        .filter(Prediction.user_id == user.id)\
        .order_by(Prediction.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    total = db.query(Prediction).filter(Prediction.user_id == user.id).count()
    
    return {
        'user': user.username,
        'total': total,
        'limit': limit,
        'skip': skip,
        'predictions': [
            {
                'id': p.id,
                'company': p.company,
                'year': p.year,
                'transmission': p.transmission,
                'km_driven': p.km_driven,
                'predicted_price': f'{p.predicted_price:,.2f}',
                'created_at': p.created_at.isoformat()
            }
            for p in predictions
        ]
    }


@router.get('/predictions/{prediction_id}')
def get_prediction_detail(
    prediction_id: int,
    user: User = Depends(get_current_user),
    _: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific prediction
    Requires: Authorization header with Bearer token and X-API-Key header
    """
    prediction = db.query(Prediction)\
        .filter(Prediction.id == prediction_id)\
        .first()
    
    if not prediction:
        return {'error': 'Prediction not found'}
    
    # Check if user owns this prediction (optional security check)
    if prediction.user_id != user.id and not user.is_admin:
        return {'error': 'Access denied'}
    
    return {
        'id': prediction.id,
        'user': user.username,
        'car_details': {
            'company': prediction.company,
            'year': prediction.year,
            'owner': prediction.owner,
            'fuel': prediction.fuel,
            'seller_type': prediction.seller_type,
            'transmission': prediction.transmission,
            'km_driven': prediction.km_driven,
            'mileage_mpg': prediction.mileage_mpg,
            'engine_cc': prediction.engine_cc,
            'max_power_bhp': prediction.max_power_bhp,
            'torque_nm': prediction.torque_nm,
            'seats': prediction.seats
        },
        'predicted_price': f'{prediction.predicted_price:,.2f}',
        'model_version': prediction.model_version,
        'created_at': prediction.created_at.isoformat()
    }


@router.get('/predictions/stats/summary')
def get_predictions_stats(
    user: User = Depends(get_current_user),
    _: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics of user's predictions
    Requires: Authorization header with Bearer token and X-API-Key header
    """
    from sqlalchemy import func
    
    stats = db.query(
        func.count(Prediction.id).label('total_predictions'),
        func.avg(Prediction.predicted_price).label('avg_price'),
        func.min(Prediction.predicted_price).label('min_price'),
        func.max(Prediction.predicted_price).label('max_price')
    ).filter(Prediction.user_id == user.id).first()
    
    return {
        'user': user.username,
        'total_predictions': stats.total_predictions or 0,
        'average_price': f'{stats.avg_price:,.2f}' if stats.avg_price else '0.00',
        'min_price': f'{stats.min_price:,.2f}' if stats.min_price else '0.00',
        'max_price': f'{stats.max_price:,.2f}' if stats.max_price else '0.00'
    }


@router.get('/model/info')
def get_model_information(
    _: str = Depends(get_api_key)
):
    """
    Get ML model information
    Requires: X-API-Key header only (no user authentication needed)
    """
    return get_model_info()