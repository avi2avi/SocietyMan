#!/usr/bin/env python
import requests
import time
import json

BASE = "http://127.0.0.1:8000/api/v1"
EMAIL = "admin@gmail.com"
PASSWORD = "Admin@123"
CODE_FILE = "scripts/last_admin_code.txt"


def read_code():
    try:
        with open(CODE_FILE) as f:
            content = f.read().strip()
            if ':' in content:
                email, code = content.split(':')
                if email.strip() == EMAIL:
                    return code.strip()
    except Exception as e:
        print('Could not read code file:', e)
    return None


def login_and_get_token():
    s = requests.Session()
    r = s.post(f"{BASE}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    print('login status', r.status_code, r.text)
    data = r.json()
    if data.get('verification_required'):
        code = read_code()
        if not code:
            print('No verification code available')
            return None
        rv = s.post(f"{BASE}/auth/verify", json={"email": EMAIL, "code": code})
        print('verify status', rv.status_code, rv.text)
        if rv.status_code == 200:
            return rv.json().get('access_token')
        return None
    else:
        return data.get('access_token')


def fetch(token, path):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}{path}", headers=headers)
    print(path, r.status_code)
    try:
        print(json.dumps(r.json(), indent=2)[:2000])
    except Exception:
        print(r.text[:1000])


if __name__ == '__main__':
    token = login_and_get_token()
    if not token:
        print('Failed to get token')
        exit(1)
    print('Token length', len(token))
    fetch(token, '/dashboard/admin/societies')
    fetch(token, '/dashboard/admin/users')
