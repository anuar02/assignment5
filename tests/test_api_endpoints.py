"""
Integration tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Database

client = TestClient(app)


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self):
        """Test that root endpoint returns health check"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "version" in data


class TestSensorDataEndpoint:
    """Test sensor data submission endpoint"""
    
    def test_post_valid_sensor_data(self):
        """Test posting valid sensor data"""
        sensor_data = {
            "bin_id": "BIN-TEST-001",
            "fill_level": 65.0,
            "temperature": 22.0,
            "weight_kg": 10.5,
            "location": "TestWard"
        }
        
        response = client.post("/api/sensor-data", json=sensor_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["bin_id"] == "BIN-TEST-001"
        assert data["message"] == "Sensor data received successfully"
    
    def test_post_critical_sensor_data_generates_alert(self):
        """Test that critical fill level generates alert"""
        sensor_data = {
            "bin_id": "BIN-TEST-002",
            "fill_level": 96.0,
            "temperature": 22.0,
            "weight_kg": 18.0,
            "location": "ICU"
        }
        
        response = client.post("/api/sensor-data", json=sensor_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "alert" in data
        assert data["alert"]["level"] == "critical"
    
    def test_post_invalid_fill_level(self):
        """Test that invalid fill level is rejected"""
        sensor_data = {
            "bin_id": "BIN-TEST-003",
            "fill_level": 150.0,  # Invalid: > 100
            "temperature": 22.0,
            "weight_kg": 10.0,
            "location": "Ward"
        }
        
        response = client.post("/api/sensor-data", json=sensor_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_post_missing_required_field(self):
        """Test that missing required field is rejected"""
        sensor_data = {
            "bin_id": "BIN-TEST-004",
            "fill_level": 50.0,
            # Missing temperature, weight_kg, location
        }
        
        response = client.post("/api/sensor-data", json=sensor_data)
        
        assert response.status_code == 422


class TestBinsEndpoint:
    """Test bins listing and details endpoints"""
    
    def setup_method(self):
        """Setup test data before each test"""
        # Post some sensor data first
        sensor_data = {
            "bin_id": "BIN-SETUP-001",
            "fill_level": 55.0,
            "temperature": 22.0,
            "weight_kg": 9.0,
            "location": "TestWard"
        }
        client.post("/api/sensor-data", json=sensor_data)
    
    def test_get_all_bins(self):
        """Test getting list of all bins"""
        response = client.get("/api/bins")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "bin_id" in data[0]
            assert "location" in data[0]
            assert "current_fill_level" in data[0]
    
    def test_get_bin_details(self):
        """Test getting details for specific bin"""
        # First create a bin
        sensor_data = {
            "bin_id": "BIN-DETAIL-001",
            "fill_level": 45.0,
            "temperature": 21.0,
            "weight_kg": 7.5,
            "location": "ER"
        }
        client.post("/api/sensor-data", json=sensor_data)
        
        # Then get its details
        response = client.get("/api/bins/BIN-DETAIL-001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["bin_id"] == "BIN-DETAIL-001"
        assert data["location"] == "ER"
    
    def test_get_nonexistent_bin(self):
        """Test getting details for non-existent bin"""
        response = client.get("/api/bins/BIN-NONEXISTENT")
        
        assert response.status_code == 404


class TestMarkBinEmptied:
    """Test marking bin as emptied"""
    
    def test_mark_existing_bin_emptied(self):
        """Test marking existing bin as emptied"""
        # First create a bin with high fill level
        sensor_data = {
            "bin_id": "BIN-EMPTY-001",
            "fill_level": 85.0,
            "temperature": 22.0,
            "weight_kg": 15.0,
            "location": "Ward"
        }
        client.post("/api/sensor-data", json=sensor_data)
        
        # Mark it as emptied
        response = client.post("/api/bins/BIN-EMPTY-001/empty")
        
        assert response.status_code == 200
        data = response.json()
        assert "emptied" in data["message"].lower()
        
        # Verify bin is now at 0% fill level
        bin_response = client.get("/api/bins/BIN-EMPTY-001")
        bin_data = bin_response.json()
        assert bin_data["current_fill_level"] == 0
    
    def test_mark_nonexistent_bin_emptied(self):
        """Test marking non-existent bin as emptied"""
        response = client.post("/api/bins/BIN-NONEXISTENT/empty")
        
        assert response.status_code == 404


class TestAlertsEndpoint:
    """Test alerts endpoint"""
    
    def test_get_active_alerts(self):
        """Test getting active alerts"""
        # Generate an alert by posting critical data
        sensor_data = {
            "bin_id": "BIN-ALERT-001",
            "fill_level": 97.0,
            "temperature": 22.0,
            "weight_kg": 18.0,
            "location": "ICU"
        }
        client.post("/api/sensor-data", json=sensor_data)
        
        # Get active alerts
        response = client.get("/api/alerts")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_all_alerts(self):
        """Test getting all alerts including resolved"""
        response = client.get("/api/alerts?active_only=false")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestStatisticsEndpoint:
    """Test statistics endpoint"""
    
    def test_get_statistics(self):
        """Test getting system statistics"""
        response = client.get("/api/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_bins" in data
        assert "active_alerts" in data
        assert "bins_needing_collection" in data
        assert "average_fill_level" in data
        assert isinstance(data["total_bins"], int)
        assert isinstance(data["average_fill_level"], (int, float))


class TestDeleteBin:
    """Test bin deletion"""
    
    def test_delete_existing_bin(self):
        """Test deleting existing bin"""
        # Create a bin first
        sensor_data = {
            "bin_id": "BIN-DELETE-001",
            "fill_level": 50.0,
            "temperature": 22.0,
            "weight_kg": 8.0,
            "location": "Ward"
        }
        client.post("/api/sensor-data", json=sensor_data)
        
        # Delete it
        response = client.delete("/api/bins/BIN-DELETE-001")
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()
    
    def test_delete_nonexistent_bin(self):
        """Test deleting non-existent bin"""
        response = client.delete("/api/bins/BIN-NONEXISTENT")
        
        assert response.status_code == 404
