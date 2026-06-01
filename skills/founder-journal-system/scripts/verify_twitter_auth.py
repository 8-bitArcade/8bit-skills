#!/usr/bin/env python3
"""Verify Twitter API v2 OAuth1 credentials from ~/.hermes/.env."""
import sys
import os

def main():
    env = {}
    env_path = os.path.expanduser("~/.hermes/.env")
    
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k] = v.strip('"')
    
    required = ["{{TW_API_KEY_VAR}}", "{{TW_API_SECRET_VAR}}", "{{TW_ACCESS_TOKEN_VAR}}", "{{TW_ACCESS_SECRET_VAR}}"]
    missing = [k for k in required if k not in env]
    
    if missing:
        print(f"✗ Missing credentials: {', '.join(missing)}")
        return 1
    
    print("✓ All 4 credentials present")
    
    try:
        from requests_oauthlib import OAuth1
        import requests
        
        auth = OAuth1(
            env["{{TW_API_KEY_VAR}}"],
            client_secret=env["{{TW_API_SECRET_VAR}}"],
            resource_owner_key=env["{{TW_ACCESS_TOKEN_VAR}}"],
            resource_owner_secret=env["{{TW_ACCESS_SECRET_VAR}}"]
        )
        
        r = requests.get("https://api.x.com/2/users/me", auth=auth)
        
        if r.status_code == 200:
            data = r.json()["data"]
            print(f"✓ Auth OK — @{data['username']} (ID: {data['id']})")
            return 0
        else:
            print(f"✗ Auth failed: {r.status_code}")
            print(f"  {r.text[:200]}")
            return 1
    except ImportError:
        print("✗ requests-oauthlib not installed. Run: pip install requests-oauthlib")
        return 1

if __name__ == "__main__":
    sys.exit(main())