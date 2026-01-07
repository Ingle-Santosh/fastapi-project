"""
Database models (tables) for SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """User table"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    predictions = relationship("Prediction", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}')>"


class Prediction(Base):
    """Prediction history table"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Car details
    company = Column(String(50))
    year = Column(Integer)
    owner = Column(String(20))
    fuel = Column(String(20))
    seller_type = Column(String(20))
    transmission = Column(String(20))
    km_driven = Column(Integer)
    mileage_mpg = Column(Float)
    engine_cc = Column(Integer)
    max_power_bhp = Column(Float)
    torque_nm = Column(Float)
    seats = Column(Integer)
    
    # Prediction result
    predicted_price = Column(Float, nullable=False)
    model_version = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="predictions")
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, company='{self.company}', price={self.predicted_price})>"