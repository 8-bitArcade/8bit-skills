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
    
    required = ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET"]
    missing = [k for k in required if k not in env]
    
    if missing:
        print(f"✗ Missing credentials: {', '.join(missing)}")
        return 1
    
    print("✓ All 4 credentials present")
    
    try:
        from requests_oauthlib import OAuth1
        import requests
        
        auth = OAuth1(
            env["TWITTER_API_KEY"],
            client_secret=env["TWITTER_API_SECRET"],
            resource_owner_key=env["TWITTER_ACCESS_TOKEN"],
            resource_owner_secret=env["TWITTER_ACCESS_TOKEN_SECRET"]
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