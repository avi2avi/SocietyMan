import requests
BASE = "http://127.0.0.1:8000/api/v1"
email = "avinash210790@gmail.com"
try:
    with open('scripts/last_admin_code.txt') as f:
        content = f.read().strip()
        e, code = content.split(':')
        if e != email:
            print('code file email mismatch', e)
        else:
            resp = requests.post(f"{BASE}/auth/verify", json={"email": email, "code": code, "new_password": "NewPass@123"})
            print('verify resp', resp.status_code, resp.text)
except FileNotFoundError:
    print('code file not found')
