import requests
import json

API_BASE = "http://localhost:8000/api/v1"

print("=== Testing Full Admin Login & Data Flow ===\n")

# Step 1: Login
print("1. Admin login...")
login_res = requests.post(f"{API_BASE}/auth/login", json={
    "email": "admin@gmail.com",
    "password": "Admin@123"
})
print(f"   Status: {login_res.status_code}")

if login_res.status_code != 200:
    print("   ERROR: Login failed")
    exit(1)

# Get verification code
print("\n2. Getting verification code...")
with open("scripts/last_admin_code.txt", "r") as f:
    code = f.read().strip().split(":")[-1]
    print(f"   Code: {code}")

# Step 3: Verify
print("\n3. Verifying admin...")
verify_res = requests.post(f"{API_BASE}/auth/verify", json={
    "email": "admin@gmail.com",
    "code": code
})
print(f"   Status: {verify_res.status_code}")

if verify_res.status_code != 200:
    print("   ERROR: Verification failed")
    print(f"   Response: {verify_res.json()}")
    exit(1)

token = verify_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"   Token: {token[:50]}...")

# Step 4: Test /users/me
print("\n4. Fetching current user profile...")
me_res = requests.get(f"{API_BASE}/users/me", headers=headers)
print(f"   Status: {me_res.status_code}")
if me_res.status_code == 200:
    profile = me_res.json()
    print(f"   User: {profile['email']} ({profile['role']})")
else:
    print(f"   ERROR: {me_res.json()}")

# Step 5: Test admin endpoints
print("\n5. Testing admin endpoints...")

endpoints = [
    ("/dashboard/admin/summary", "Admin summary"),
    ("/dashboard/admin/users", "Admin users list"),
    ("/dashboard/admin/societies", "Admin societies list"),
    ("/dashboard/admin/db-info", "Database info"),
    ("/societies/pending", "Pending societies"),
    ("/users/pending", "Pending residents"),
]

for endpoint, label in endpoints:
    res = requests.get(f"{API_BASE}{endpoint}", headers=headers)
    status_str = "✓" if res.status_code == 200 else "✗"
    print(f"   {status_str} {label}: {res.status_code}")
    if res.status_code != 200:
        print(f"     Error: {res.json().get('detail', 'Unknown error')}")

print("\n=== All tests completed ===")
