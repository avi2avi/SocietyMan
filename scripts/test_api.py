import requests

BASE = "http://127.0.0.1:8000/api/v1"

# Test society registration
society = {
    "name": "Test Society",
    "address": "123 Test Lane",
    "city": "Testville",
    "state": "TS",
    "pincode": "123456",
}
resp = requests.post(f"{BASE}/societies", json=society)
print("Create society status:", resp.status_code)
try:
    print(resp.json())
except Exception:
    print(resp.text)

# Note: admin login flow requires an existing user; skip further tests here.
