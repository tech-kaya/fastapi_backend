from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class PlaceBase(BaseModel):
    place_id: str
    name: str
    address: str
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None


class PlaceCreate(PlaceBase):
    pass


class Place(PlaceBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    stored_at: Optional[datetime] = None


class UserBase(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: Optional[datetime] = None


class FormSubmissionBase(BaseModel):
    place_id: int
    user_id: int
    website_url: str
    submission_status: str = "pending"
    error_message: Optional[str] = None


class FormSubmissionCreate(FormSubmissionBase):
    pass


class FormSubmission(FormSubmissionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    submitted_at: Optional[datetime] = None
    place: Optional[Place] = None
    user: Optional[User] = None


class FormSubmissionStatus(BaseModel):
    total_submissions: int
    successful: int
    failed: int
    pending: int
    recent_submissions: list[FormSubmission]


# Simplified schemas for API responses that match the expected workflow
class PlaceSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    website: Optional[str] = None  # Using actual DB column name


class FormSubmissionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    place_id: int
    website_url: str
    submission_status: str
    submitted_at: Optional[datetime] = None 