"""
Simple in-memory database module
For production, replace with PostgreSQL/MongoDB
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from app.models import BinStatus


class Database:
    """Simple in-memory database for storing sensor readings, bins, and alerts"""
    
    def __init__(self):
        self.sensor_readings: List[Dict[str, Any]] = []
        self.bins: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []
    
    def save_sensor_reading(self, reading: Dict[str, Any]) -> None:
        """
        Save a sensor reading to the database
        
        Args:
            reading: Dictionary containing sensor reading data
        """
        self.sensor_readings.append(reading)
        
        # Update bin information
        bin_id = reading["bin_id"]
        if bin_id not in self.bins:
            self.bins[bin_id] = {
                "bin_id": bin_id,
                "location": reading["location"],
                "current_fill_level": reading["fill_level"],
                "current_weight_kg": reading["weight_kg"],
                "current_temperature": reading["temperature"],
                "status": reading["status"],
                "last_updated": reading["timestamp"],
                "last_emptied": None,
                "total_readings": 1
            }
        else:
            self.bins[bin_id].update({
                "current_fill_level": reading["fill_level"],
                "current_weight_kg": reading["weight_kg"],
                "current_temperature": reading["temperature"],
                "status": reading["status"],
                "last_updated": reading["timestamp"],
                "total_readings": self.bins[bin_id].get("total_readings", 0) + 1
            })
    
    def get_all_bins(self) -> List[Dict[str, Any]]:
        """
        Get list of all bins
        
        Returns:
            List of bin dictionaries
        """
        return list(self.bins.values())
    
    def get_bin_by_id(self, bin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get bin information by ID
        
        Args:
            bin_id: Unique bin identifier
        
        Returns:
            Bin dictionary or None if not found
        """
        bin_data = self.bins.get(bin_id)
        if not bin_data:
            return None
        
        # Add recent readings
        recent_readings = [
            r for r in self.sensor_readings[-10:]
            if r["bin_id"] == bin_id
        ]
        
        bin_data["recent_readings"] = recent_readings
        return bin_data
    
    def save_alert(self, alert: Dict[str, Any]) -> None:
        """
        Save an alert to the database
        
        Args:
            alert: Alert dictionary
        """
        self.alerts.append(alert)
    
    def get_alerts(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get alerts from the database
        
        Args:
            active_only: If True, return only unresolved alerts
        
        Returns:
            List of alert dictionaries
        """
        if active_only:
            return [a for a in self.alerts if not a.get("resolved", False)]
        return self.alerts
    
    def mark_bin_emptied(self, bin_id: str) -> None:
        """
        Mark a bin as emptied
        
        Args:
            bin_id: Unique bin identifier
        """
        if bin_id in self.bins:
            self.bins[bin_id].update({
                "current_fill_level": 0,
                "current_weight_kg": 0,
                "status": BinStatus.NORMAL.value,
                "last_emptied": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            })
            
            # Add a sensor reading for the empty bin
            empty_reading = {
                "bin_id": bin_id,
                "timestamp": datetime.now().isoformat(),
                "fill_level": 0,
                "temperature": self.bins[bin_id].get("current_temperature", 20.0),
                "weight_kg": 0,
                "location": self.bins[bin_id]["location"],
                "status": BinStatus.NORMAL.value,
                "needs_attention": False,
                "temperature_alert": False
            }
            self.sensor_readings.append(empty_reading)
    
    def resolve_alerts_for_bin(self, bin_id: str) -> None:
        """
        Resolve all active alerts for a specific bin
        
        Args:
            bin_id: Unique bin identifier
        """
        now = datetime.now().isoformat()
        for alert in self.alerts:
            if alert["bin_id"] == bin_id and not alert.get("resolved", False):
                alert["resolved"] = True
                alert["resolved_at"] = now
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall system statistics
        
        Returns:
            Dictionary with statistics
        """
        total_bins = len(self.bins)
        active_alerts = len([a for a in self.alerts if not a.get("resolved", False)])
        
        bins_needing_collection = sum(
            1 for bin_data in self.bins.values()
            if bin_data.get("status") in [BinStatus.CRITICAL.value, BinStatus.FULL.value]
        )
        
        if total_bins > 0:
            avg_fill_level = sum(
                b.get("current_fill_level", 0) for b in self.bins.values()
            ) / total_bins
        else:
            avg_fill_level = 0
        
        # Calculate total waste collected (sum of all emptied bins)
        total_waste_collected = sum(
            r.get("weight_kg", 0) for r in self.sensor_readings
            if r.get("fill_level", 100) == 0  # Readings when bin was emptied
        )
        
        return {
            "total_bins": total_bins,
            "active_alerts": active_alerts,
            "bins_needing_collection": bins_needing_collection,
            "average_fill_level": round(avg_fill_level, 2),
            "total_waste_collected_kg": round(total_waste_collected, 2),
            "total_readings": len(self.sensor_readings),
            "total_alerts_generated": len(self.alerts),
            "last_updated": datetime.now().isoformat()
        }
    
    def delete_bin(self, bin_id: str) -> bool:
        """
        Delete a bin from the system
        
        Args:
            bin_id: Unique bin identifier
        
        Returns:
            True if deleted, False if not found
        """
        if bin_id in self.bins:
            del self.bins[bin_id]
            
            # Remove associated sensor readings
            self.sensor_readings = [
                r for r in self.sensor_readings if r["bin_id"] != bin_id
            ]
            
            # Resolve associated alerts
            self.resolve_alerts_for_bin(bin_id)
            
            return True
        return False
    
    def clear_all_data(self) -> None:
        """Clear all data from the database (for testing)"""
        self.sensor_readings.clear()
        self.bins.clear()
        self.alerts.clear()
