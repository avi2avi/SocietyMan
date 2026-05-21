#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Society360 Enhanced Features
Tests all new endpoints with sample data
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any

class Society360APITester:
    def __init__(self, base_url: str = "http://localhost:8000", token: str = None):
        self.base_url = base_url
        self.api_prefix = "/api"
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}" if token else "",
            "Content-Type": "application/json"
        }
        self.results = []

    def log_result(self, test_name: str, endpoint: str, method: str, status_code: int, success: bool, response: Dict = None):
        """Log test result"""
        self.results.append({
            "test": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response": response if not success else None
        })
        status_icon = "✓" if success else "✗"
        print(f"  {status_icon} {test_name}: {status_code}")

    def print_summary(self):
        """Print test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed
        
        print("\n" + "="*60)
        print(f"TEST SUMMARY: {passed}/{total} passed")
        print("="*60)
        
        for result in self.results:
            if not result["success"]:
                print(f"❌ {result['test']}")
                print(f"   Endpoint: {result['endpoint']}")
                print(f"   Status: {result['status_code']}")
                if result['response']:
                    print(f"   Error: {result['response'].get('detail', 'Unknown error')}")

    # ============================================================
    # MAINTENANCE TESTS
    # ============================================================

    def test_maintenance_categories(self):
        """Test maintenance category creation and listing"""
        print("\n--- Testing Maintenance Categories ---")

        # Create category
        payload = {
            "name": "Plumbing",
            "description": "Water supply and drainage issues",
            "icon": "🚰",
            "color": "#3b82f6",
            "sort_order": 1
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/maintenance/categories",
                json=payload,
                headers=self.headers
            )
            success = response.status_code == 200
            self.log_result("Create Category", "/maintenance/categories", "POST", response.status_code, success)
            
            if success:
                self.category_id = response.json().get("id")
                return response.json()
        except Exception as e:
            self.log_result("Create Category", "/maintenance/categories", "POST", 0, False, {"detail": str(e)})
            return None

    def test_list_categories(self):
        """Test listing maintenance categories"""
        print("  Testing list categories...")
        try:
            response = requests.get(
                f"{self.base_url}{self.api_prefix}/maintenance/categories",
                headers=self.headers
            )
            success = response.status_code == 200
            self.log_result("List Categories", "/maintenance/categories", "GET", response.status_code, success)
            return response.json() if success else None
        except Exception as e:
            self.log_result("List Categories", "/maintenance/categories", "GET", 0, False, {"detail": str(e)})

    def test_work_logs(self, ticket_id: int = 1):
        """Test adding work logs"""
        print("  Testing work logs...")
        payload = {
            "staff_user_id": 2,
            "description": "Fixed water leakage in bathroom. Replaced faulty pipe.",
            "hours_spent": 2.5
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/maintenance/{ticket_id}/work-logs",
                json=payload,
                headers=self.headers
            )
            success = response.status_code == 200
            self.log_result("Add Work Log", f"/maintenance/{ticket_id}/work-logs", "POST", response.status_code, success)
            return response.json() if success else None
        except Exception as e:
            self.log_result("Add Work Log", f"/maintenance/{ticket_id}/work-logs", "POST", 0, False, {"detail": str(e)})

    def test_rating(self, ticket_id: int = 1):
        """Test rating maintenance work"""
        print("  Testing ratings...")
        payload = {
            "rating": 4.5,
            "feedback": "Work was completed on time with good quality. Very satisfied with the service."
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/maintenance/{ticket_id}/rate",
                json=payload,
                headers=self.headers
            )
            success = response.status_code in [200, 201]
            self.log_result("Rate Maintenance", f"/maintenance/{ticket_id}/rate", "POST", response.status_code, success)
            return response.json() if success else None
        except Exception as e:
            self.log_result("Rate Maintenance", f"/maintenance/{ticket_id}/rate", "POST", 0, False, {"detail": str(e)})

    # ============================================================
    # COMMUNICATION TESTS
    # ============================================================

    def test_announcements(self):
        """Test creating announcements"""
        print("\n--- Testing Announcements ---")
        
        payload = {
            "title": "Water Supply Maintenance",
            "content": "Water supply will be interrupted tomorrow from 10 AM to 2 PM for maintenance work.",
            "announcement_type": "notice",
            "priority": "high"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/communications/announcements",
                json=payload,
                headers=self.headers
            )
            success = response.status_code == 200
            self.log_result("Create Announcement", "/communications/announcements", "POST", response.status_code, success)
            
            if success:
                self.announcement_id = response.json().get("id")
                return response.json()
        except Exception as e:
            self.log_result("Create Announcement", "/communications/announcements", "POST", 0, False, {"detail": str(e)})

    def test_list_announcements(self):
        """Test listing announcements"""
        print("  Testing list announcements...")
        try:
            response = requests.get(
                f"{self.base_url}{self.api_prefix}/communications/announcements",
                headers=self.headers
            )
            success = response.status_code == 200
            self.log_result("List Announcements", "/communications/announcements", "GET", response.status_code, success)
            return response.json() if success else None
        except Exception as e:
            self.log_result("List Announcements", "/communications/announcements", "GET", 0, False, {"detail": str(e)})

    def test_forum_posts(self):
        """Test creating forum posts"""
        print("\n--- Testing Forum ---")
        
        payload = {
            "title": "Parking issues in Block A",
            "content": "Residents are facing parking issues in Block A. Need to discuss better parking management.",
            "category": "general",
            "tags": "parking,block-a,issues"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/communications/forum",
                json=payload,
                headers=self.headers
            )
            success = response.status_code == 200
            self.log_result("Create Forum Post", "/communications/forum", "POST", response.status_code, success)
            
            if success:
                self.post_id = response.json().get("id")
                return response.json()
        except Exception as e:
            self.log_result("Create Forum Post", "/communications/forum", "POST", 0, False, {"detail": str(e)})

    def test_list_forum(self):
        """Test listing forum posts"""
        print("  Testing list forum posts...")
        try:
            response = requests.get(
                f"{self.base_url}{self.api_prefix}/communications/forum",
                headers=self.headers
            )
            success = response.status_code == 200
            self.log_result("List Forum Posts", "/communications/forum", "GET", response.status_code, success)
            return response.json() if success else None
        except Exception as e:
            self.log_result("List Forum Posts", "/communications/forum", "GET", 0, False, {"detail": str(e)})

    # ============================================================
    # VISITOR TESTS
    # ============================================================

    def test_visitor_pre_register(self, visitor_log_id: int = 1):
        """Test visitor pre-registration"""
        print("\n--- Testing Visitor Management ---")
        
        payload = {
            "visitor_log_id": visitor_log_id,
            "vehicle_number": "MH02AB1234",
            "vehicle_type": "car",
            "parking_slot": "A-101"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/visitors/enhanced/pre-register",
                json=payload,
                headers=self.headers
            )
            success = response.status_code in [200, 201]
            self.log_result("Pre-Register Visitor", "/visitors/enhanced/pre-register", "POST", response.status_code, success)
            
            if success:
                self.approval_id = response.json().get("id")
                return response.json()
        except Exception as e:
            self.log_result("Pre-Register Visitor", "/visitors/enhanced/pre-register", "POST", 0, False, {"detail": str(e)})

    def test_pending_approvals(self):
        """Test listing pending approvals"""
        print("  Testing pending approvals...")
        try:
            response = requests.get(
                f"{self.base_url}{self.api_prefix}/visitors/enhanced/pending-approvals",
                headers=self.headers
            )
            success = response.status_code == 200
            self.log_result("List Pending Approvals", "/visitors/enhanced/pending-approvals", "GET", response.status_code, success)
            return response.json() if success else None
        except Exception as e:
            self.log_result("List Pending Approvals", "/visitors/enhanced/pending-approvals", "GET", 0, False, {"detail": str(e)})

    def test_visitor_history(self):
        """Test visitor history"""
        print("  Testing visitor history...")
        try:
            response = requests.get(
                f"{self.base_url}{self.api_prefix}/visitors/enhanced/history",
                headers=self.headers
            )
            success = response.status_code == 200
            self.log_result("Get Visitor History", "/visitors/enhanced/history", "GET", response.status_code, success)
            return response.json() if success else None
        except Exception as e:
            self.log_result("Get Visitor History", "/visitors/enhanced/history", "GET", 0, False, {"detail": str(e)})

    # ============================================================
    # AMENITIES TESTS
    # ============================================================

    def test_create_amenity(self):
        """Test creating amenities"""
        print("\n--- Testing Amenities ---")
        
        payload = {
            "name": "Community Hall",
            "description": "Spacious hall for community events and gatherings",
            "capacity": 100,
            "location": "Building A, Ground Floor",
            "rules": "No outside food. Cleanup after use is mandatory.",
            "booking_price": 500
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/amenities",
                json=payload,
                headers=self.headers
            )
            success = response.status_code in [200, 201]
            self.log_result("Create Amenity", "/amenities", "POST", response.status_code, success)
            
            if success:
                self.amenity_id = response.json().get("id")
                return response.json()
        except Exception as e:
            self.log_result("Create Amenity", "/amenities", "POST", 0, False, {"detail": str(e)})

    def test_list_amenities(self):
        """Test listing amenities"""
        print("  Testing list amenities...")
        try:
            response = requests.get(
                f"{self.base_url}{self.api_prefix}/amenities",
                headers=self.headers
            )
            success = response.status_code == 200
            self.log_result("List Amenities", "/amenities", "GET", response.status_code, success)
            return response.json() if success else None
        except Exception as e:
            self.log_result("List Amenities", "/amenities", "GET", 0, False, {"detail": str(e)})

    def test_amenity_booking(self, amenity_id: int = 1):
        """Test booking amenity"""
        print("  Testing amenity booking...")
        
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        payload = {
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat(),
            "purpose": "Birthday celebration",
            "notes": "Party for 50 people"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/amenities/{amenity_id}/bookings",
                json=payload,
                headers=self.headers
            )
            success = response.status_code in [200, 201]
            self.log_result("Book Amenity", f"/amenities/{amenity_id}/bookings", "POST", response.status_code, success)
            return response.json() if success else None
        except Exception as e:
            self.log_result("Book Amenity", f"/amenities/{amenity_id}/bookings", "POST", 0, False, {"detail": str(e)})

    def test_amenity_availability(self, amenity_id: int = 1):
        """Test checking amenity availability"""
        print("  Testing availability check...")
        
        start_time = (datetime.now() + timedelta(days=2)).isoformat()
        end_time = (datetime.now() + timedelta(days=2, hours=3)).isoformat()
        
        try:
            response = requests.get(
                f"{self.base_url}{self.api_prefix}/amenities/{amenity_id}/availability",
                params={"start_datetime": start_time, "end_datetime": end_time},
                headers=self.headers
            )
            success = response.status_code == 200
            self.log_result("Check Availability", f"/amenities/{amenity_id}/availability", "GET", response.status_code, success)
            return response.json() if success else None
        except Exception as e:
            self.log_result("Check Availability", f"/amenities/{amenity_id}/availability", "GET", 0, False, {"detail": str(e)})

    def test_usage_stats(self, amenity_id: int = 1):
        """Test amenity usage statistics"""
        print("  Testing usage stats...")
        try:
            response = requests.get(
                f"{self.base_url}{self.api_prefix}/amenities/{amenity_id}/usage-stats",
                headers=self.headers
            )
            success = response.status_code == 200
            self.log_result("Get Usage Stats", f"/amenities/{amenity_id}/usage-stats", "GET", response.status_code, success)
            return response.json() if success else None
        except Exception as e:
            self.log_result("Get Usage Stats", f"/amenities/{amenity_id}/usage-stats", "GET", 0, False, {"detail": str(e)})

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("SOCIETY360 API TEST SUITE")
        print("="*60)
        
        # Run all test groups
        self.test_maintenance_categories()
        self.test_list_categories()
        self.test_work_logs()
        self.test_rating()
        
        self.test_announcements()
        self.test_list_announcements()
        self.test_forum_posts()
        self.test_list_forum()
        
        self.test_visitor_pre_register()
        self.test_pending_approvals()
        self.test_visitor_history()
        
        self.test_create_amenity()
        self.test_list_amenities()
        self.test_amenity_booking()
        self.test_amenity_availability()
        self.test_usage_stats()
        
        # Print summary
        self.print_summary()

if __name__ == "__main__":
    import sys
    
    # Get token from environment or command line
    token = "your_admin_token_here"  # Replace with actual token
    
    # Create tester instance
    tester = Society360APITester(token=token)
    
    # Run all tests
    tester.run_all_tests()
    
    # Export results to JSON
    with open("api_test_results.json", "w") as f:
        json.dump(tester.results, f, indent=2)
    
    print("\n✓ Test results saved to api_test_results.json")
