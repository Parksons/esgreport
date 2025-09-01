#!/usr/bin/env python3
"""
Test script for the ESG Report API
Run this to test the API endpoints
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on localhost:8000")
        return False

def test_send_otp():
    """Test sending OTP"""
    print("\n🔍 Testing send OTP...")
    test_data = {
        "email": "test@example.com",
        "name": "Test User",
        "company": "Test Company"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/send-otp",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Send OTP endpoint working")
            print(f"   Response: {response.json()}")
            return True
        elif response.status_code == 429:
            print("⚠️  Rate limited (expected if testing multiple times)")
            return True
        else:
            print(f"❌ Send OTP failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing send OTP: {e}")
        return False

def test_invalid_otp():
    """Test invalid OTP verification"""
    print("\n🔍 Testing invalid OTP verification...")
    test_data = {
        "email": "test@example.com",
        "otp": "000000"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/verify-otp",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ Invalid OTP correctly rejected")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing invalid OTP: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 ESG Report API Test Suite")
    print("=" * 40)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Health check failed. Please start the server first.")
        return
    
    # Test send OTP
    test_send_otp()
    
    # Test invalid OTP
    test_invalid_otp()
    
    print("\n✅ Test suite completed!")
    print("\n💡 To test with real OTP:")
    print("   1. Use the send-otp endpoint with a real email")
    print("   2. Check the email for the OTP")
    print("   3. Use the verify-otp endpoint with the received OTP")

if __name__ == "__main__":
    main()
