import requests
import time
BASE = "http://127.0.0.1:8000/api/v1"

email = "admin@gmail.com"
password = "Admin@123"

# Login
resp = requests.post(f"{BASE}/auth/login", json={"email": email, "password": password})
print('login status', resp.status_code, resp.text)

if resp.status_code == 200:
    data = resp.json()
    if data.get('verification_required'):
        print('Verification required, waiting for code file...')
        # wait a bit for server to write file
        for i in range(10):
            try:
                with open('scripts/last_admin_code.txt') as f:
                    content = f.read().strip()
                    if content:
                        e, code = content.split(':')
                        if e == email:
                            print('Found code:', code)
                            # now verify
                            vresp = requests.post(f"{BASE}/auth/verify", json={"email": email, "code": code})
                            print('verify status', vresp.status_code, vresp.text)
                            break
            except FileNotFoundError:
                pass
            time.sleep(0.5)

