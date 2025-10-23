"""
Alert generation module
Creates and manages alerts for waste collection
"""

from app.models import Alert, AlertLevel
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


def generate_alert_if_needed(processed_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Generate alert if sensor data indicates need for action
    
    Args:
        processed_data: Dictionary with processed sensor data
    
    Returns:
        Alert dictionary if alert needed, None otherwise
    """
    if not processed_data["needs_attention"]:
        return None
    
    # Determine alert type and level
    if processed_data["fill_level"] >= 95:
        return create_alert(
            bin_id=processed_data["bin_id"],
            alert_type="bin_full",
            level=AlertLevel.CRITICAL,
            message=f"URGENT: Bin {processed_data['bin_id']} is {processed_data['fill_level']:.1f}% full and must be emptied immediately!",
            location=processed_data["location"]
        )
    
    elif processed_data["fill_level"] >= 80:
        return create_alert(
            bin_id=processed_data["bin_id"],
            alert_type="high_fill_level",
            level=AlertLevel.HIGH,
            message=f"Bin {processed_data['bin_id']} is {processed_data['fill_level']:.1f}% full and requires collection soon",
            location=processed_data["location"]
        )
    
    elif processed_data["temperature_alert"]:
        return create_alert(
            bin_id=processed_data["bin_id"],
            alert_type="temperature_alert",
            level=AlertLevel.MEDIUM,
            message=f"Temperature alert for bin {processed_data['bin_id']}: {processed_data['temperature']:.1f}°C (safe range: 15-30°C)",
            location=processed_data["location"]
        )
    
    return None


def create_alert(
    bin_id: str,
    alert_type: str,
    level: AlertLevel,
    message: str,
    location: str
) -> Dict[str, Any]:
    """
    Create a new alert
    
    Args:
        bin_id: Unique identifier for the bin
        alert_type: Type of alert (bin_full, high_fill_level, temperature_alert)
        level: Alert severity level
        message: Human-readable alert message
        location: Physical location of the bin
    
    Returns:
        Dictionary containing alert information
    """
    alert_id = generate_alert_id(bin_id)
    
    alert = {
        "alert_id": alert_id,
        "bin_id": bin_id,
        "alert_type": alert_type,
        "level": level.value,
        "message": message,
        "location": location,
        "timestamp": datetime.now().isoformat(),
        "resolved": False,
        "resolved_at": None
    }
    
    return alert


def generate_alert_id(bin_id: str) -> str:
    """
    Generate unique alert ID
    
    Args:
        bin_id: Bin identifier
    
    Returns:
        Unique alert ID string
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"ALT-{bin_id}-{timestamp}-{unique_id}"


def should_escalate_alert(alert: Dict[str, Any], time_unresolved_hours: float) -> bool:
    """
    Determine if an alert should be escalated based on time unresolved
    
    Args:
        alert: Alert dictionary
        time_unresolved_hours: Hours since alert was created
    
    Returns:
        True if alert should be escalated, False otherwise
    """
    escalation_thresholds = {
        AlertLevel.CRITICAL: 1.0,  # Escalate after 1 hour
        AlertLevel.HIGH: 4.0,       # Escalate after 4 hours
        AlertLevel.MEDIUM: 12.0,    # Escalate after 12 hours
        AlertLevel.LOW: 24.0        # Escalate after 24 hours
    }
    
    alert_level = AlertLevel(alert["level"])
    threshold = escalation_thresholds.get(alert_level, 24.0)
    
    return time_unresolved_hours >= threshold


def resolve_alert(alert_id: str) -> Dict[str, Any]:
    """
    Mark an alert as resolved
    
    Args:
        alert_id: Unique alert identifier
    
    Returns:
        Updated alert dictionary
    """
    return {
        "alert_id": alert_id,
        "resolved": True,
        "resolved_at": datetime.now().isoformat()
    }


def get_alert_summary(alerts: list) -> Dict[str, Any]:
    """
    Generate summary statistics for a list of alerts
    
    Args:
        alerts: List of alert dictionaries
    
    Returns:
        Dictionary with alert statistics
    """
    if not alerts:
        return {
            "total_alerts": 0,
            "by_level": {},
            "by_type": {},
            "unresolved": 0
        }
    
    summary = {
        "total_alerts": len(alerts),
        "by_level": {},
        "by_type": {},
        "unresolved": sum(1 for a in alerts if not a.get("resolved", False))
    }
    
    # Count by level
    for alert in alerts:
        level = alert.get("level", "unknown")
        summary["by_level"][level] = summary["by_level"].get(level, 0) + 1
        
        alert_type = alert.get("alert_type", "unknown")
        summary["by_type"][alert_type] = summary["by_type"].get(alert_type, 0) + 1
    
    return summary


def prioritize_alerts(alerts: list) -> list:
    """
    Sort alerts by priority (level and timestamp)
    
    Args:
        alerts: List of alert dictionaries
    
    Returns:
        Sorted list of alerts (highest priority first)
    """
    level_priority = {
        AlertLevel.CRITICAL.value: 4,
        AlertLevel.HIGH.value: 3,
        AlertLevel.MEDIUM.value: 2,
        AlertLevel.LOW.value: 1
    }
    
    def alert_priority(alert):
        level = alert.get("level", "low")
        priority = level_priority.get(level, 0)
        # Higher priority alerts and older alerts come first
        return (-priority, alert.get("timestamp", ""))
    
    return sorted(alerts, key=alert_priority)
