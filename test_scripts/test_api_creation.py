#!/usr/bin/env python3
"""
Quick test script to check if API key creation endpoint is working
"""
import requests
import json

def test_api_key_creation():
    # First, we need to get session cookies by visiting the login page
    session = requests.Session()
    
    # Get CSRF token
    login_page = session.get('http://127.0.0.1:8002/login/')
    if login_page.status_code != 200:
        print(f"❌ Failed to load login page: {login_page.status_code}")
        return
    
    # Extract CSRF token from the login page
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if not csrf_token:
        print("❌ Could not find CSRF token")
        return
    
    csrf_value = csrf_token.get('value')
    print(f"✅ Got CSRF token: {csrf_value[:10]}...")
    
    # Test the API key creation endpoint directly
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_value,
        'Referer': 'http://127.0.0.1:8002/dashboard/'
    }
    
    data = {
        'name': 'Test API Key'
    }
    
    response = session.post(
        'http://127.0.0.1:8002/api-keys/create/',
        headers=headers,
        data=json.dumps(data)
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response content: {response.text}")

if __name__ == "__main__":
    print("🧪 Testing API key creation endpoint...")
    try:
        test_api_key_creation()
    except ImportError:
        print("⚠️  This test requires beautifulsoup4: pip install beautifulsoup4")
    except Exception as e:
        print(f"❌ Error: {e}")
