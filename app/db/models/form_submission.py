from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base


class Place(Base):
    __tablename__ = "places"
    
    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    address = Column(Text, nullable=False)
    city = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    category = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    website = Column(Text, nullable=True)
    stored_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    
    form_submissions = relationship("FormSubmission", back_populates="place")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    
    form_submissions = relationship("FormSubmission", back_populates="user")


class FormSubmission(Base):
    __tablename__ = "form_submission"
    
    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    website_url = Column(String(500), nullable=False)
    submission_status = Column(String(50), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    
    place = relationship("Place", back_populates="form_submissions")
    user = relationship("User", back_populates="form_submissions") 