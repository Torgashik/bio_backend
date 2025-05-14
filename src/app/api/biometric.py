from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from ..database.database import get_db
from ..models.models import User, BiometricData, AccessLog, UserRole, BiometricDataType
from ..schemas.schemas import (
    BiometricDataBase,
    BiometricDataCreate,
    BiometricDataResponse,
    BiometricDataUpdate,
    AccessLog as AccessLogSchema,
    AnalyticsResponse
)
from ..utils.auth import get_current_user, check_permissions
from ..utils.analytics import analyze_biometric_data, analyze_access_patterns
from ..config import settings

router = APIRouter()

@router.post("/", response_model=BiometricDataResponse)
async def create_biometric_data(
    data: BiometricDataCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must be associated with an organization"
        )
    
    biometric_data = BiometricData(
        user_id=current_user.id,
        data_type=data.data_type,
        value=data.value,
        timestamp=data.timestamp or datetime.utcnow(),
        data_metadata=data.data_metadata,
        organization_id=current_user.organization_id
    )
    db.add(biometric_data)
    db.commit()
    db.refresh(biometric_data)
    
    log = AccessLog(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        action="create",
        details={"data_id": biometric_data.id}
    )
    db.add(log)
    db.commit()
    
    return biometric_data

@router.get("/{data_id}", response_model=BiometricDataResponse)
async def get_biometric_data(
    data_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    biometric_data = db.query(BiometricData).filter(BiometricData.id == data_id).first()
    if not biometric_data:
        raise HTTPException(status_code=404, detail="Biometric data not found")
    
    if biometric_data.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this data")
    
    log = AccessLog(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        action="read",
        details={"data_id": data_id}
    )
    db.add(log)
    db.commit()
    
    return biometric_data

@router.put("/{data_id}", response_model=BiometricDataResponse)
async def update_biometric_data(
    data_id: int,
    data: BiometricDataUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    biometric_data = db.query(BiometricData).filter(BiometricData.id == data_id).first()
    if not biometric_data:
        raise HTTPException(status_code=404, detail="Biometric data not found")
    
    if biometric_data.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this data")
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(biometric_data, field, value)
    
    db.commit()
    db.refresh(biometric_data)
    return biometric_data

@router.delete("/{data_id}")
async def delete_biometric_data(
    data_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    biometric_data = db.query(BiometricData).filter(BiometricData.id == data_id).first()
    if not biometric_data:
        raise HTTPException(status_code=404, detail="Biometric data not found")
    
    if biometric_data.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this data")
    
    db.delete(biometric_data)
    db.commit()
    return {"message": "Biometric data deleted successfully"}

@router.get("/", response_model=List[BiometricDataResponse])
async def list_biometric_data(
    data_type: Optional[BiometricDataType] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(BiometricData).filter(BiometricData.organization_id == current_user.organization_id)
    if data_type:
        query = query.filter(BiometricData.data_type == data_type)
    return query.all()

@router.get("/analytics/", response_model=AnalyticsResponse)
async def get_analytics(
    data_type: BiometricDataType,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must be associated with an organization"
        )
    
    data = db.query(BiometricData).filter(
        BiometricData.organization_id == current_user.organization_id,
        BiometricData.data_type == data_type
    ).all()
    
    if not data:
        raise HTTPException(status_code=404, detail="No data found for analysis")
    
    values = [d.value for d in data]
    return {
        "data_type": data_type,
        "count": len(values),
        "average": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
        "metadata": {
            "organization_id": current_user.organization_id,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    }

@router.get("/access-logs/", response_model=List[AccessLogSchema])
async def get_access_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[AccessLogSchema]:
    if not check_permissions(current_user.role, UserRole.ORGANIZATION):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    logs = db.query(AccessLog).all()
    return logs

@router.get("/access-analytics/", response_model=dict)
async def get_access_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    if not check_permissions(current_user.role, UserRole.ORGANIZATION):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    logs = db.query(AccessLog).all()
    return analyze_access_patterns([{
        "id": log.id,
        "organization_id": log.organization_id,
        "user_id": log.user_id,
        "action": log.action,
        "timestamp": log.timestamp,
        "details": log.details
    } for log in logs]) 