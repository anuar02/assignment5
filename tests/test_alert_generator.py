"""
Unit tests for alert_generator module
"""

import pytest
from app.alert_generator import (
    generate_alert_if_needed,
    create_alert,
    should_escalate_alert,
    get_alert_summary,
    prioritize_alerts
)
from app.models import AlertLevel


class TestGenerateAlertIfNeeded:
    """Test alert generation logic"""
    
    def test_no_alert_for_normal_bin(self):
        """Test that no alert is generated for normal bin"""
        data = {
            "bin_id": "BIN-001",
            "fill_level": 45.0,
            "temperature": 22.0,
            "location": "Ward",
            "needs_attention": False,
            "temperature_alert": False
        }
        
        alert = generate_alert_if_needed(data)
        assert alert is None
    
    def test_critical_alert_for_full_bin(self):
        """Test critical alert for bin >= 95% full"""
        data = {
            "bin_id": "BIN-002",
            "fill_level": 97.0,
            "temperature": 22.0,
            "location": "ICU",
            "needs_attention": True,
            "temperature_alert": False
        }
        
        alert = generate_alert_if_needed(data)
        
        assert alert is not None
        assert alert["bin_id"] == "BIN-002"
        assert alert["alert_type"] == "bin_full"
        assert alert["level"] == AlertLevel.CRITICAL.value
        assert "URGENT" in alert["message"]
    
    def test_high_alert_for_critical_bin(self):
        """Test high alert for bin 80-94% full"""
        data = {
            "bin_id": "BIN-003",
            "fill_level": 85.0,
            "temperature": 22.0,
            "location": "ER",
            "needs_attention": True,
            "temperature_alert": False
        }
        
        alert = generate_alert_if_needed(data)
        
        assert alert is not None
        assert alert["alert_type"] == "high_fill_level"
        assert alert["level"] == AlertLevel.HIGH.value
    
    def test_temperature_alert(self):
        """Test alert for temperature outside safe range"""
        data = {
            "bin_id": "BIN-004",
            "fill_level": 50.0,
            "temperature": 35.0,
            "location": "Ward",
            "needs_attention": True,
            "temperature_alert": True
        }
        
        alert = generate_alert_if_needed(data)
        
        assert alert is not None
        assert alert["alert_type"] == "temperature_alert"
        assert alert["level"] == AlertLevel.MEDIUM.value
        assert "Temperature alert" in alert["message"]


class TestCreateAlert:
    """Test alert creation"""
    
    def test_create_alert_structure(self):
        """Test that created alert has correct structure"""
        alert = create_alert(
            bin_id="BIN-TEST",
            alert_type="test_alert",
            level=AlertLevel.HIGH,
            message="Test message",
            location="TestLocation"
        )
        
        assert "alert_id" in alert
        assert alert["bin_id"] == "BIN-TEST"
        assert alert["alert_type"] == "test_alert"
        assert alert["level"] == AlertLevel.HIGH.value
        assert alert["message"] == "Test message"
        assert alert["location"] == "TestLocation"
        assert "timestamp" in alert
        assert alert["resolved"] == False
        assert alert["resolved_at"] is None
    
    def test_alert_id_uniqueness(self):
        """Test that alert IDs are unique"""
        alert1 = create_alert("BIN-001", "test", AlertLevel.LOW, "Test", "Loc1")
        alert2 = create_alert("BIN-001", "test", AlertLevel.LOW, "Test", "Loc1")
        
        assert alert1["alert_id"] != alert2["alert_id"]


class TestShouldEscalateAlert:
    """Test alert escalation logic"""
    
    def test_critical_alert_escalation(self):
        """Test that critical alerts escalate after 1 hour"""
        alert = {"level": AlertLevel.CRITICAL.value}
        
        assert should_escalate_alert(alert, 0.5) == False
        assert should_escalate_alert(alert, 1.0) == True
        assert should_escalate_alert(alert, 2.0) == True
    
    def test_high_alert_escalation(self):
        """Test that high alerts escalate after 4 hours"""
        alert = {"level": AlertLevel.HIGH.value}
        
        assert should_escalate_alert(alert, 3.0) == False
        assert should_escalate_alert(alert, 4.0) == True
        assert should_escalate_alert(alert, 5.0) == True
    
    def test_medium_alert_escalation(self):
        """Test that medium alerts escalate after 12 hours"""
        alert = {"level": AlertLevel.MEDIUM.value}
        
        assert should_escalate_alert(alert, 10.0) == False
        assert should_escalate_alert(alert, 12.0) == True
    
    def test_low_alert_escalation(self):
        """Test that low alerts escalate after 24 hours"""
        alert = {"level": AlertLevel.LOW.value}
        
        assert should_escalate_alert(alert, 20.0) == False
        assert should_escalate_alert(alert, 24.0) == True


class TestGetAlertSummary:
    """Test alert summary generation"""
    
    def test_empty_alerts(self):
        """Test summary with no alerts"""
        summary = get_alert_summary([])
        
        assert summary["total_alerts"] == 0
        assert summary["unresolved"] == 0
    
    def test_alert_summary_counts(self):
        """Test summary counts by level and type"""
        alerts = [
            {
                "level": AlertLevel.CRITICAL.value,
                "alert_type": "bin_full",
                "resolved": False
            },
            {
                "level": AlertLevel.HIGH.value,
                "alert_type": "high_fill_level",
                "resolved": False
            },
            {
                "level": AlertLevel.CRITICAL.value,
                "alert_type": "bin_full",
                "resolved": True
            }
        ]
        
        summary = get_alert_summary(alerts)
        
        assert summary["total_alerts"] == 3
        assert summary["unresolved"] == 2
        assert summary["by_level"][AlertLevel.CRITICAL.value] == 2
        assert summary["by_level"][AlertLevel.HIGH.value] == 1
        assert summary["by_type"]["bin_full"] == 2
        assert summary["by_type"]["high_fill_level"] == 1


class TestPrioritizeAlerts:
    """Test alert prioritization"""
    
    def test_prioritize_by_level(self):
        """Test that alerts are sorted by priority level"""
        alerts = [
            {
                "level": AlertLevel.LOW.value,
                "timestamp": "2025-01-01T10:00:00"
            },
            {
                "level": AlertLevel.CRITICAL.value,
                "timestamp": "2025-01-01T11:00:00"
            },
            {
                "level": AlertLevel.HIGH.value,
                "timestamp": "2025-01-01T09:00:00"
            }
        ]
        
        prioritized = prioritize_alerts(alerts)
        
        # Critical should be first
        assert prioritized[0]["level"] == AlertLevel.CRITICAL.value
        # High should be second
        assert prioritized[1]["level"] == AlertLevel.HIGH.value
        # Low should be last
        assert prioritized[2]["level"] == AlertLevel.LOW.value
    
    def test_prioritize_by_timestamp_same_level(self):
        """Test that alerts with same level are sorted by timestamp"""
        alerts = [
            {
                "level": AlertLevel.HIGH.value,
                "timestamp": "2025-01-01T12:00:00"
            },
            {
                "level": AlertLevel.HIGH.value,
                "timestamp": "2025-01-01T10:00:00"
            }
        ]
        
        prioritized = prioritize_alerts(alerts)
        
        # Older alert (earlier timestamp) should come first
        assert prioritized[0]["timestamp"] < prioritized[1]["timestamp"]
