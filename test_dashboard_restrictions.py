#!/usr/bin/env python3
"""
Test script to verify that the dashboard Recent Activity section is properly restricted for free users
"""
import requests
from bs4 import BeautifulSoup
import sys

def test_dashboard_restrictions():
    """Test the dashboard restrictions for different user types"""
    base_url = "http://127.0.0.1:8000"
    
    # Test data
    test_users = [
        {
            'username': 'testuser',
            'password': 'testpass123',
            'plan': 'free',
            'expected_restriction': True
        },
        {
            'username': 'premiumuser', 
            'password': 'premiumpass123',
            'plan': 'developer',
            'expected_restriction': False
        }
    ]
    
    print("🧪 Testing Dashboard Recent Activity Restrictions\n")
    
    for user_data in test_users:
        print(f"Testing {user_data['username']} ({user_data['plan']} plan)...")
        
        # Create session
        session = requests.Session()
        
        # Get login page and CSRF token
        login_page = session.get(f"{base_url}/login/")
        if login_page.status_code != 200:
            print(f"❌ Failed to load login page: {login_page.status_code}")
            continue
            
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_token:
            print(f"❌ Could not find CSRF token")
            continue
            
        # Login
        login_data = {
            'username': user_data['username'],
            'password': user_data['password'],
            'csrfmiddlewaretoken': csrf_token.get('value')
        }
        
        login_response = session.post(f"{base_url}/login/", data=login_data)
        
        if login_response.status_code != 302:  # Should redirect after successful login
            print(f"❌ Login failed for {user_data['username']}")
            continue
            
        # Get dashboard page
        dashboard_response = session.get(f"{base_url}/dashboard/")
        if dashboard_response.status_code != 200:
            print(f"❌ Failed to load dashboard: {dashboard_response.status_code}")
            continue
            
        # Parse dashboard content
        dashboard_soup = BeautifulSoup(dashboard_response.content, 'html.parser')
        
        # Check for Recent Activity section restrictions
        recent_activity_section = dashboard_soup.find(text="Recent Activity")
        if not recent_activity_section:
            print(f"❌ Could not find Recent Activity section")
            continue
            
        # Look for restriction indicators
        has_blur_filter = "filter blur-sm" in dashboard_response.text
        has_premium_overlay = "Premium Feature" in dashboard_response.text
        has_upgrade_button = "Upgrade Plan" in dashboard_response.text
        
        if user_data['expected_restriction']:
            # Free user should see restrictions
            if has_blur_filter and has_premium_overlay and has_upgrade_button:
                print(f"✅ {user_data['username']}: Restrictions properly applied")
                print(f"   - Blur filter: ✅")
                print(f"   - Premium overlay: ✅") 
                print(f"   - Upgrade button: ✅")
            else:
                print(f"❌ {user_data['username']}: Restrictions missing")
                print(f"   - Blur filter: {'✅' if has_blur_filter else '❌'}")
                print(f"   - Premium overlay: {'✅' if has_premium_overlay else '❌'}")
                print(f"   - Upgrade button: {'✅' if has_upgrade_button else '❌'}")
        else:
            # Premium user should NOT see restrictions
            if not has_blur_filter and not has_premium_overlay:
                print(f"✅ {user_data['username']}: No restrictions (as expected)")
                print(f"   - Content accessible: ✅")
            else:
                print(f"❌ {user_data['username']}: Unexpected restrictions found")
                print(f"   - Blur filter: {'❌ (unexpected)' if has_blur_filter else '✅'}")
                print(f"   - Premium overlay: {'❌ (unexpected)' if has_premium_overlay else '✅'}")
        
        print()

if __name__ == "__main__":
    test_dashboard_restrictions()
