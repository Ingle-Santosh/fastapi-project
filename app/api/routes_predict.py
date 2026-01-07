from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.dependencies import get_api_key, get_current_user
from app.services.model_service import predict_car_price
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.database.models import Prediction

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

@router.post('/predict')
def predict_price(car: CarFeatures, user = Depends(get_current_user), _ = Depends(get_api_key),
                  db: Session = Depends(get_db)):
    """
    Predict car price and save to database
    """
    prediction = predict_car_price(car.model_dump())
    db_prediction = Prediction(
        user_id=user.id if hasattr(user, 'id') else None,
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
        'saved_at': db_prediction.created_at
    }

@router.get('/predictions/history')
def get_prediction_history(
    user = Depends(get_current_user),
    _ = Depends(get_api_key),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Get user's prediction history
    """
    user_id = user.id if hasattr(user, 'id') else None
    
    if user_id:
        predictions = db.query(Prediction)\
            .filter(Prediction.user_id == user_id)\
            .order_by(Prediction.created_at.desc())\
            .limit(limit)\
            .all()
    else:
        predictions = db.query(Prediction)\
            .order_by(Prediction.created_at.desc())\
            .limit(limit)\
            .all()
    
    return {
        'total': len(predictions),
        'predictions': [
            {
                'id': p.id,
                'company': p.company,
                'year': p.year,
                'predicted_price': f'{p.predicted_price:,.2f}',
                'created_at': p.created_at
            }
            for p in predictions
        ]
    }

@router.get('/predictions/{prediction_id}')
def get_prediction_detail(
    prediction_id: int,
    user = Depends(get_current_user),
    _ = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific prediction
    """
    prediction = db.query(Prediction)\
        .filter(Prediction.id == prediction_id)\
        .first()
    
    if not prediction:
        return {'error': 'Prediction not found'}
    
    return {
        'id': prediction.id,
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
        'created_at': prediction.created_at
    }


@router.get('/predictions/stats/summary')
def get_predictions_stats(
    user = Depends(get_current_user),
    _ = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics of predictions
    """
    from sqlalchemy import func
    
    stats = db.query(
        func.count(Prediction.id).label('total_predictions'),
        func.avg(Prediction.predicted_price).label('avg_price'),
        func.min(Prediction.predicted_price).label('min_price'),
        func.max(Prediction.predicted_price).label('max_price')
    ).first()
    
    return {
        'total_predictions': stats.total_predictions or 0,
        'average_price': f'{stats.avg_price:,.2f}' if stats.avg_price else '0.00',
        'min_price': f'{stats.min_price:,.2f}' if stats.min_price else '0.00',
        'max_price': f'{stats.max_price:,.2f}' if stats.max_price else '0.00'
    }