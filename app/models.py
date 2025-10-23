"""
Data models for the Medical Waste Monitoring API
Using Pydantic for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class BinStatus(str, Enum):
    """Enum for bin status"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    FULL = "full"


class AlertLevel(str, Enum):
    """Enum for alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SensorData(BaseModel):
    """Model for incoming sensor data from IoT devices"""
    bin_id: str = Field(..., description="Unique identifier for the waste bin")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    fill_level: float = Field(..., ge=0, le=100, description="Fill level percentage (0-100)")
    temperature: float = Field(..., description="Temperature in Celsius")
    weight_kg: float = Field(..., ge=0, description="Weight in kilograms")
    location: str = Field(..., description="Physical location of the bin")
    
    @validator('fill_level')
    def validate_fill_level(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Fill level must be between 0 and 100')
        return v
    
    @validator('weight_kg')
    def validate_weight(cls, v):
        if v < 0:
            raise ValueError('Weight cannot be negative')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "bin_id": "BIN-ICU-001",
                "timestamp": "2025-10-23T14:30:00Z",
                "fill_level": 75.5,
                "temperature": 22.5,
                "weight_kg": 12.3,
                "location": "ICU-Floor3"
            }
        }


class Bin(BaseModel):
    """Model for waste bin information"""
    bin_id: str
    location: str
    current_fill_level: float
    current_weight_kg: float
    current_temperature: float
    status: BinStatus
    last_updated: str
    last_emptied: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "bin_id": "BIN-ICU-001",
                "location": "ICU-Floor3",
                "current_fill_level": 75.5,
                "current_weight_kg": 12.3,
                "current_temperature": 22.5,
                "status": "warning",
                "last_updated": "2025-10-23T14:30:00Z",
                "last_emptied": "2025-10-23T08:00:00Z"
            }
        }


class Alert(BaseModel):
    """Model for waste collection alerts"""
    alert_id: str
    bin_id: str
    alert_type: str
    level: AlertLevel
    message: str
    timestamp: str
    resolved: bool = False
    resolved_at: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "alert_id": "ALT-001-20251023",
                "bin_id": "BIN-ICU-001",
                "alert_type": "high_fill_level",
                "level": "high",
                "message": "Bin BIN-ICU-001 is 85% full and requires collection",
                "timestamp": "2025-10-23T14:30:00Z",
                "resolved": False,
                "resolved_at": None
            }
        }


class ProcessedSensorData(BaseModel):
    """Model for processed sensor data with calculated status"""
    bin_id: str
    timestamp: str
    fill_level: float
    temperature: float
    weight_kg: float
    location: str
    status: BinStatus
    needs_attention: bool
    temperature_alert: bool


class Statistics(BaseModel):
    """Model for system statistics"""
    total_bins: int
    active_alerts: int
    bins_needing_collection: int
    average_fill_level: float
    total_waste_collected_kg: float
    last_updated: str
