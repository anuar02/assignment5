"""
Sensor data processing module
Handles validation, processing, and status determination for sensor readings
"""

from app.models import SensorData, BinStatus, ProcessedSensorData
from typing import Dict, Any


def process_sensor_data(data: SensorData) -> Dict[str, Any]:
    """
    Process incoming sensor data and determine bin status
    
    Args:
        data: SensorData object from IoT device
    
    Returns:
        Dictionary with processed data including status
    """
    # Determine bin status based on fill level
    status = determine_bin_status(data.fill_level)
    
    # Check if temperature is abnormal (outside safe range 15-30°C)
    temperature_alert = check_temperature_alert(data.temperature)
    
    # Determine if bin needs immediate attention
    needs_attention = (
        status in [BinStatus.CRITICAL, BinStatus.FULL] or 
        temperature_alert
    )
    
    processed_data = {
        "bin_id": data.bin_id,
        "timestamp": data.timestamp,
        "fill_level": data.fill_level,
        "temperature": data.temperature,
        "weight_kg": data.weight_kg,
        "location": data.location,
        "status": status.value,
        "needs_attention": needs_attention,
        "temperature_alert": temperature_alert
    }
    
    return processed_data


def determine_bin_status(fill_level: float) -> BinStatus:
    """
    Determine bin status based on fill level
    
    Args:
        fill_level: Fill level percentage (0-100)
    
    Returns:
        BinStatus enum value
    """
    if fill_level >= 95:
        return BinStatus.FULL
    elif fill_level >= 80:
        return BinStatus.CRITICAL
    elif fill_level >= 60:
        return BinStatus.WARNING
    else:
        return BinStatus.NORMAL


def check_temperature_alert(temperature: float) -> bool:
    """
    Check if temperature is outside safe range
    Medical waste should be stored between 15-30°C
    
    Args:
        temperature: Temperature in Celsius
    
    Returns:
        True if temperature is outside safe range, False otherwise
    """
    TEMP_MIN = 15.0
    TEMP_MAX = 30.0
    
    return temperature < TEMP_MIN or temperature > TEMP_MAX


def check_bin_status(bin_id: str, fill_level: float) -> Dict[str, Any]:
    """
    Check the current status of a bin
    
    Args:
        bin_id: Unique identifier for the bin
        fill_level: Current fill level percentage
    
    Returns:
        Dictionary with bin status information
    """
    status = determine_bin_status(fill_level)
    
    return {
        "bin_id": bin_id,
        "status": status.value,
        "fill_level": fill_level,
        "requires_collection": status in [BinStatus.CRITICAL, BinStatus.FULL]
    }


def validate_sensor_data(data: Dict[str, Any]) -> bool:
    """
    Validate sensor data for completeness and accuracy
    
    Args:
        data: Dictionary containing sensor data
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["bin_id", "fill_level", "temperature", "weight_kg", "location"]
    
    # Check all required fields are present
    for field in required_fields:
        if field not in data:
            return False
    
    # Validate ranges
    if not (0 <= data["fill_level"] <= 100):
        return False
    
    if data["weight_kg"] < 0:
        return False
    
    return True


def calculate_time_to_full(current_fill_level: float, fill_rate_per_hour: float) -> float:
    """
    Estimate time until bin is full based on current fill rate
    
    Args:
        current_fill_level: Current fill level percentage
        fill_rate_per_hour: Estimated fill rate per hour (percentage points)
    
    Returns:
        Estimated hours until bin is full
    """
    if fill_rate_per_hour <= 0:
        return float('inf')
    
    remaining_capacity = 100 - current_fill_level
    hours_to_full = remaining_capacity / fill_rate_per_hour
    
    return hours_to_full


def get_collection_priority(fill_level: float, location: str) -> int:
    """
    Calculate collection priority based on fill level and location
    
    Args:
        fill_level: Current fill level percentage
        location: Physical location of the bin
    
    Returns:
        Priority score (1-10, where 10 is highest priority)
    """
    # Base priority on fill level
    if fill_level >= 95:
        priority = 10
    elif fill_level >= 80:
        priority = 8
    elif fill_level >= 60:
        priority = 5
    else:
        priority = 2
    
    # Increase priority for critical locations
    critical_locations = ["ICU", "ER", "OR", "Surgery"]
    if any(loc in location for loc in critical_locations):
        priority = min(10, priority + 2)
    
    return priority
