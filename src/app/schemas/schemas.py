from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.models import UserRole, BiometricDataType

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    organization_id: int

class UserResponse(UserBase):
    id: int
    role: UserRole
    organization_id: int

    class Config:
        from_attributes = True

class OrganizationBase(BaseModel):
    name: str
    contact_email: EmailStr

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None

class OrganizationResponse(OrganizationBase):
    id: int

    class Config:
        from_attributes = True

class BiometricDataBase(BaseModel):
    data_type: BiometricDataType
    value: float
    timestamp: datetime
    data_metadata: Dict[str, Any]

class BiometricDataCreate(BiometricDataBase):
    pass

class BiometricDataUpdate(BaseModel):
    value: Optional[float] = None
    timestamp: Optional[datetime] = None
    data_metadata: Optional[Dict[str, Any]] = None

class BiometricDataResponse(BiometricDataBase):
    id: int
    user_id: int
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AccessLogBase(BaseModel):
    action: str
    details: Dict[str, Any]

class AccessLogCreate(AccessLogBase):
    pass

class AccessLog(AccessLogBase):
    id: int
    user_id: int
    organization_id: Optional[int]
    timestamp: datetime

    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    data_type: BiometricDataType
    count: int
    average: float
    min: float
    max: float
    metadata: Dict[str, Any] 