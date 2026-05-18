#!/usr/bin/env python
"""Comprehensive data seeding script for SocietyMan"""
import sys
sys.path.insert(0, '.')

import requests
import json
import time

BASE = "http://127.0.0.1:8000/api/v1"
EMAIL = "admin@gmail.com"
PASSWORD = "Admin@123"

def login_and_get_token():
    """Login and get JWT token"""
    # First, login to get verification code
    login_response = requests.post(
        f"{BASE}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    
    print(f"Login response: {login_response.status_code}")
    login_data = login_response.json()
    print(json.dumps(login_data, indent=2))
    
    if login_data.get('verification_required'):
        # Wait for code file
        print("Waiting for verification code...")
        for i in range(10):
            try:
                with open('scripts/last_admin_code.txt') as f:
                    content = f.read().strip()
                    if content and ':' in content:
                        email, code = content.split(':')
                        if email == EMAIL:
                            print(f"Found verification code: {code}")
                            # Verify and get token
                            verify_response = requests.post(
                                f"{BASE}/auth/verify",
                                json={"email": EMAIL, "code": code}
                            )
                            print(f"Verify response: {verify_response.status_code}")
                            verify_data = verify_response.json()
                            
                            if verify_response.status_code == 200:
                                token = verify_data.get('access_token')
                                print(f"Token received: {token[:20]}...")
                                return token
                            else:
                                print(f"Verification failed: {verify_data}")
            except FileNotFoundError:
                pass
            time.sleep(0.5)
    
    raise Exception("Could not get verification token")

def seed_data(token):
    """Call comprehensive seed endpoint"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\nCalling comprehensive seed endpoint...")
    response = requests.post(
        f"{BASE}/erp/demo/comprehensive-seed",
        headers=headers
    )
    
    print(f"Seed response: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    if response.status_code == 200:
        return data
    else:
        raise Exception(f"Seeding failed: {data}")

if __name__ == "__main__":
    try:
        print("Starting comprehensive data seeding...\n")
        token = login_and_get_token()
        result = seed_data(token)
        print("\n✅ Seeding completed successfully!")
        print(f"\nSummary:")
        print(f"  Societies: {result['data']['societies_created']}")
        print(f"  Members: {result['data']['total_members']}")
        print(f"  Visitor Logs: {result['data']['total_visitor_logs']}")
        print(f"  Bills: {result['data']['total_bills']}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
