#!/usr/bin/env python3
"""
Integration tests for E-learning Platform API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_api_endpoints():
    """Test basic API endpoints"""
    
    print("🔍 Testing API endpoints...")
    
    # Test API root
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ API Root endpoint working")
            data = response.json()
            print(f"   API Version: {data.get('version', 'Unknown')}")
        else:
            print(f"❌ API Root failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API Root error: {e}")
    
    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/health/")
        if response.status_code == 200:
            print("✅ Health check endpoint working")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test platform stats
    try:
        response = requests.get(f"{BASE_URL}/stats/")
        if response.status_code == 200:
            print("✅ Platform stats endpoint working")
            data = response.json()
            print(f"   Total users: {data.get('users', {}).get('total', 0)}")
            print(f"   Total courses: {data.get('courses', {}).get('total', 0)}")
        else:
            print(f"❌ Platform stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Platform stats error: {e}")
    
    # Test course categories
    try:
        response = requests.get(f"{BASE_URL}/courses/categories/")
        if response.status_code == 200:
            print("✅ Course categories endpoint working")
        else:
            print(f"❌ Course categories failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Course categories error: {e}")
    
    # Test course list
    try:
        response = requests.get(f"{BASE_URL}/courses/")
        if response.status_code == 200:
            print("✅ Course list endpoint working")
            data = response.json()
            print(f"   Total courses: {data.get('count', 0)}")
        else:
            print(f"❌ Course list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Course list error: {e}")

def test_user_registration():
    """Test user registration flow"""
    
    print("\n👤 Testing user registration...")
    
    user_data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "user_type": "student"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
        if response.status_code == 201:
            print("✅ User registration working")
            data = response.json()
            if 'access' in data and 'refresh' in data:
                print("✅ JWT tokens generated successfully")
                return data['access']
            else:
                print("❌ JWT tokens not found in response")
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ User registration error: {e}")
    
    return None

if __name__ == "__main__":
    print("🧪 E-learning Platform Integration Tests")
    print("=" * 50)
    print("⚠️  Make sure the Django server is running on localhost:8000")
    print("   Run: python manage.py runserver")
    print()
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    # Run tests
    test_api_endpoints()
    access_token = test_user_registration()
    
    print("\n" + "=" * 50)
    print("🎯 Integration tests completed!")
    print("\n📚 Next steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Access admin panel: http://localhost:8000/admin/")
    print("3. Test API endpoints with Postman or curl")
    print("4. Check API documentation: api_documentation.md")
