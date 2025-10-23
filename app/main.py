"""
Medical Waste Monitoring API
Main FastAPI application for receiving and processing IoT sensor data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import uvicorn

from app.models import SensorData, Bin, Alert, BinStatus
from app.sensor_handler import process_sensor_data, check_bin_status
from app.alert_generator import generate_alert_if_needed
from app.database import Database

# Initialize FastAPI app
app = FastAPI(
    title="Medical Waste Monitoring API",
    description="IoT-based system for tracking medical waste in healthcare facilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()


@app.get("/")
def read_root():
    """Root endpoint - API health check"""
    return {
        "message": "Medical Waste Monitoring API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/sensor-data", status_code=201)
def receive_sensor_data(data: SensorData):
    """
    Receive sensor data from IoT waste bins
    
    Args:
        data: SensorData object containing bin_id, fill_level, temperature, weight
    
    Returns:
        Confirmation message and any generated alerts
    """
    try:
        # Process the sensor data
        processed_data = process_sensor_data(data)
        
        # Store in database
        db.save_sensor_reading(processed_data)
        
        # Check if alert needed
        alert = generate_alert_if_needed(processed_data)
        
        response = {
            "message": "Sensor data received successfully",
            "bin_id": data.bin_id,
            "timestamp": data.timestamp,
            "status": processed_data["status"]
        }
        
        if alert:
            response["alert"] = alert
            db.save_alert(alert)
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/bins", response_model=List[Bin])
def get_all_bins():
    """
    Get list of all waste bins and their current status
    
    Returns:
        List of all bins with current status
    """
    try:
        bins = db.get_all_bins()
        return bins
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bins/{bin_id}")
def get_bin_details(bin_id: str):
    """
    Get detailed information about a specific bin
    
    Args:
        bin_id: Unique identifier for the waste bin
    
    Returns:
        Bin details including latest readings and history
    """
    try:
        bin_data = db.get_bin_by_id(bin_id)
        if not bin_data:
            raise HTTPException(status_code=404, detail=f"Bin {bin_id} not found")
        return bin_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts", response_model=List[Alert])
def get_active_alerts(active_only: bool = True):
    """
    Get list of alerts
    
    Args:
        active_only: If True, return only active alerts. If False, return all alerts.
    
    Returns:
        List of alerts
    """
    try:
        alerts = db.get_alerts(active_only=active_only)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bins/{bin_id}/empty")
def mark_bin_emptied(bin_id: str):
    """
    Mark a bin as emptied after waste collection
    
    Args:
        bin_id: Unique identifier for the waste bin
    
    Returns:
        Confirmation message
    """
    try:
        # Check if bin exists
        bin_data = db.get_bin_by_id(bin_id)
        if not bin_data:
            raise HTTPException(status_code=404, detail=f"Bin {bin_id} not found")
        
        # Update bin status
        db.mark_bin_emptied(bin_id)
        
        # Resolve any active alerts for this bin
        db.resolve_alerts_for_bin(bin_id)
        
        return {
            "message": f"Bin {bin_id} marked as emptied",
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics")
def get_statistics():
    """
    Get overall system statistics
    
    Returns:
        Dictionary containing various statistics
    """
    try:
        stats = db.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/bins/{bin_id}")
def delete_bin(bin_id: str):
    """
    Delete a bin from the system (admin function)
    
    Args:
        bin_id: Unique identifier for the waste bin
    
    Returns:
        Confirmation message
    """
    try:
        result = db.delete_bin(bin_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Bin {bin_id} not found")
        
        return {
            "message": f"Bin {bin_id} deleted successfully",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
