"""
Unit tests for sensor_handler module
"""

import pytest
from app.sensor_handler import (
    process_sensor_data,
    determine_bin_status,
    check_temperature_alert,
    validate_sensor_data,
    calculate_time_to_full,
    get_collection_priority
)
from app.models import SensorData, BinStatus


class TestDetermineBinStatus:
    """Test bin status determination logic"""
    
    def test_normal_status(self):
        """Test that fill level < 60% returns NORMAL status"""
        assert determine_bin_status(30.0) == BinStatus.NORMAL
        assert determine_bin_status(59.9) == BinStatus.NORMAL
    
    def test_warning_status(self):
        """Test that fill level 60-79% returns WARNING status"""
        assert determine_bin_status(60.0) == BinStatus.WARNING
        assert determine_bin_status(70.0) == BinStatus.WARNING
        assert determine_bin_status(79.9) == BinStatus.WARNING
    
    def test_critical_status(self):
        """Test that fill level 80-94% returns CRITICAL status"""
        assert determine_bin_status(80.0) == BinStatus.CRITICAL
        assert determine_bin_status(90.0) == BinStatus.CRITICAL
        assert determine_bin_status(94.9) == BinStatus.CRITICAL
    
    def test_full_status(self):
        """Test that fill level >= 95% returns FULL status"""
        assert determine_bin_status(95.0) == BinStatus.FULL
        assert determine_bin_status(99.0) == BinStatus.FULL
        assert determine_bin_status(100.0) == BinStatus.FULL


class TestTemperatureAlert:
    """Test temperature alert logic"""
    
    def test_normal_temperature(self):
        """Test that temperature within safe range returns False"""
        assert check_temperature_alert(20.0) == False
        assert check_temperature_alert(25.0) == False
        assert check_temperature_alert(15.0) == False
        assert check_temperature_alert(30.0) == False
    
    def test_low_temperature_alert(self):
        """Test that temperature below 15°C triggers alert"""
        assert check_temperature_alert(10.0) == True
        assert check_temperature_alert(14.9) == True
        assert check_temperature_alert(0.0) == True
    
    def test_high_temperature_alert(self):
        """Test that temperature above 30°C triggers alert"""
        assert check_temperature_alert(35.0) == True
        assert check_temperature_alert(30.1) == True
        assert check_temperature_alert(40.0) == True


class TestProcessSensorData:
    """Test sensor data processing"""
    
    def test_process_normal_data(self):
        """Test processing of normal sensor data"""
        data = SensorData(
            bin_id="BIN-TEST-001",
            fill_level=50.0,
            temperature=22.0,
            weight_kg=8.5,
            location="TestWard"
        )
        
        result = process_sensor_data(data)
        
        assert result["bin_id"] == "BIN-TEST-001"
        assert result["status"] == BinStatus.NORMAL.value
        assert result["needs_attention"] == False
        assert result["temperature_alert"] == False
    
    def test_process_critical_fill_level(self):
        """Test processing of critical fill level data"""
        data = SensorData(
            bin_id="BIN-TEST-002",
            fill_level=85.0,
            temperature=22.0,
            weight_kg=15.0,
            location="ICU"
        )
        
        result = process_sensor_data(data)
        
        assert result["status"] == BinStatus.CRITICAL.value
        assert result["needs_attention"] == True
    
    def test_process_temperature_alert(self):
        """Test processing with temperature alert"""
        data = SensorData(
            bin_id="BIN-TEST-003",
            fill_level=40.0,
            temperature=35.0,
            weight_kg=6.0,
            location="ER"
        )
        
        result = process_sensor_data(data)
        
        assert result["temperature_alert"] == True
        assert result["needs_attention"] == True


class TestValidateSensorData:
    """Test sensor data validation"""
    
    def test_valid_data(self):
        """Test validation of correct sensor data"""
        data = {
            "bin_id": "BIN-001",
            "fill_level": 75.0,
            "temperature": 22.0,
            "weight_kg": 10.0,
            "location": "ICU"
        }
        assert validate_sensor_data(data) == True
    
    def test_missing_field(self):
        """Test validation fails with missing field"""
        data = {
            "bin_id": "BIN-001",
            "fill_level": 75.0,
            "temperature": 22.0,
            # Missing weight_kg
            "location": "ICU"
        }
        assert validate_sensor_data(data) == False
    
    def test_invalid_fill_level(self):
        """Test validation fails with invalid fill level"""
        data = {
            "bin_id": "BIN-001",
            "fill_level": 150.0,  # Invalid: > 100
            "temperature": 22.0,
            "weight_kg": 10.0,
            "location": "ICU"
        }
        assert validate_sensor_data(data) == False
    
    def test_negative_weight(self):
        """Test validation fails with negative weight"""
        data = {
            "bin_id": "BIN-001",
            "fill_level": 75.0,
            "temperature": 22.0,
            "weight_kg": -5.0,  # Invalid: negative
            "location": "ICU"
        }
        assert validate_sensor_data(data) == False


class TestCalculateTimeToFull:
    """Test time-to-full calculation"""
    
    def test_normal_fill_rate(self):
        """Test calculation with normal fill rate"""
        time = calculate_time_to_full(50.0, 10.0)
        assert time == 5.0  # 50% remaining / 10% per hour
    
    def test_slow_fill_rate(self):
        """Test calculation with slow fill rate"""
        time = calculate_time_to_full(80.0, 2.0)
        assert time == 10.0  # 20% remaining / 2% per hour
    
    def test_zero_fill_rate(self):
        """Test calculation with zero fill rate returns infinity"""
        time = calculate_time_to_full(50.0, 0.0)
        assert time == float('inf')
    
    def test_negative_fill_rate(self):
        """Test calculation with negative fill rate returns infinity"""
        time = calculate_time_to_full(50.0, -1.0)
        assert time == float('inf')


class TestGetCollectionPriority:
    """Test collection priority calculation"""
    
    def test_low_priority_normal_location(self):
        """Test low priority for low fill level in normal location"""
        priority = get_collection_priority(30.0, "GeneralWard")
        assert priority == 2
    
    def test_medium_priority(self):
        """Test medium priority for warning level"""
        priority = get_collection_priority(70.0, "GeneralWard")
        assert priority == 5
    
    def test_high_priority(self):
        """Test high priority for critical level"""
        priority = get_collection_priority(85.0, "GeneralWard")
        assert priority == 8
    
    def test_critical_priority(self):
        """Test critical priority for full bin"""
        priority = get_collection_priority(98.0, "GeneralWard")
        assert priority == 10
    
    def test_critical_location_bonus(self):
        """Test priority bonus for critical location"""
        normal_priority = get_collection_priority(70.0, "GeneralWard")
        icu_priority = get_collection_priority(70.0, "ICU-Floor3")
        
        assert icu_priority > normal_priority
        assert icu_priority == min(10, normal_priority + 2)
