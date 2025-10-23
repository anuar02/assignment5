#!/usr/bin/env python3
"""
Test script to verify the Medical Waste Monitoring API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_health_check():
    """Test the health check endpoint"""
    print_section("Testing Health Check")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_submit_sensor_data():
    """Test submitting sensor data"""
    print_section("Testing Sensor Data Submission")
    
    test_data = [
        {
            "bin_id": "BIN-TEST-001",
            "fill_level": 45.0,
            "temperature": 22.0,
            "weight_kg": 8.0,
            "location": "TestWard"
        },
        {
            "bin_id": "BIN-TEST-002",
            "fill_level": 85.0,
            "temperature": 22.5,
            "weight_kg": 15.0,
            "location": "ICU"
        },
        {
            "bin_id": "BIN-TEST-003",
            "fill_level": 97.0,
            "temperature": 23.0,
            "weight_kg": 18.0,
            "location": "Emergency"
        }
    ]
    
    for data in test_data:
        print(f"\nSubmitting data for {data['bin_id']}...")
        response = requests.post(f"{BASE_URL}/api/sensor-data", json=data)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        time.sleep(0.5)
    
    return True

def test_get_bins():
    """Test getting all bins"""
    print_section("Testing Get All Bins")
    response = requests.get(f"{BASE_URL}/api/bins")
    print(f"Status Code: {response.status_code}")
    bins = response.json()
    print(f"Total bins: {len(bins)}")
    for bin_data in bins:
        print(f"\n{bin_data['bin_id']}:")
        print(f"  Location: {bin_data['location']}")
        print(f"  Fill Level: {bin_data['current_fill_level']}%")
        print(f"  Status: {bin_data['status']}")
    return response.status_code == 200

def test_get_alerts():
    """Test getting alerts"""
    print_section("Testing Get Alerts")
    response = requests.get(f"{BASE_URL}/api/alerts")
    print(f"Status Code: {response.status_code}")
    alerts = response.json()
    print(f"Active alerts: {len(alerts)}")
    for alert in alerts:
        print(f"\n{alert['alert_id']}:")
        print(f"  Bin: {alert['bin_id']}")
        print(f"  Level: {alert['level']}")
        print(f"  Message: {alert['message']}")
    return response.status_code == 200

def test_mark_bin_emptied():
    """Test marking a bin as emptied"""
    print_section("Testing Mark Bin as Emptied")
    bin_id = "BIN-TEST-003"
    print(f"Marking {bin_id} as emptied...")
    response = requests.post(f"{BASE_URL}/api/bins/{bin_id}/empty")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_get_statistics():
    """Test getting system statistics"""
    print_section("Testing Get Statistics")
    response = requests.get(f"{BASE_URL}/api/statistics")
    print(f"Status Code: {response.status_code}")
    stats = response.json()
    print(f"Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    return response.status_code == 200

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  MEDICAL WASTE MONITORING API - TEST SUITE")
    print("="*60)
    
    try:
        # Run tests
        tests = [
            ("Health Check", test_health_check),
            ("Submit Sensor Data", test_submit_sensor_data),
            ("Get All Bins", test_get_bins),
            ("Get Alerts", test_get_alerts),
            ("Mark Bin Emptied", test_mark_bin_emptied),
            ("Get Statistics", test_get_statistics),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
            except Exception as e:
                print(f"\nError in {test_name}: {e}")
                results.append((test_name, False))
        
        # Print summary
        print_section("TEST SUMMARY")
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed successfully!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API")
        print("Make sure the API is running on http://localhost:8000")
        print("\nTo start the API, run:")
        print("  uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()
