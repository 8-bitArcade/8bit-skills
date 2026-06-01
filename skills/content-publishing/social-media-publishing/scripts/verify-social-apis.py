#!/usr/bin/env python3
"""Verify social media API connections."""

import os
import sys
import requests
from requests_oauthlib import OAuth1

def load_env():
    env = {}
    with open('{{ENV_PATH}}') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k] = v.strip('"')
    return env

def test_meta(env):
    """Test Meta API connection."""
    token = env.get('{{META_TOKEN_VAR}}') or env.get('META_FACEBOOK_APP_ID')
    if not token:
        print("❌ Meta: No token found")
        return False
    
    try:
        r = requests.get('https://graph.facebook.com/v18.0/me/accounts',
                        params={'access_token': token, 'fields': 'id,name,instagram_business_account'})
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Meta: Connected ({len(data.get('data', []))} pages found)")
            return True
        else:
            print(f"❌ Meta: {r.status_code} - {r.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ Meta: {e}")
        return False

def test_x(env):
    """Test X/Twitter API connection."""
    key = env.get('{{TW_API_KEY_VAR}}')
    secret = env.get('{{TW_API_SECRET_VAR}}')
    token = env.get('{{TW_ACCESS_TOKEN_VAR}}')
    token_secret = env.get('{{TW_ACCESS_SECRET_VAR}}')
    
    if not all([key, secret, token, token_secret]):
        print("❌ X: Missing credentials")
        return False
    
    try:
        auth = OAuth1(key, client_secret=secret,
                     resource_owner_key=token,
                     resource_owner_secret=token_secret)
        r = requests.get('https://api.x.com/2/users/me', auth=auth)
        if r.status_code == 200:
            data = r.json()['data']
            print(f"✅ X: Connected (@{data['username']})")
            return True
        else:
            print(f"❌ X: {r.status_code} - {r.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ X: {e}")
        return False

def main():
    env = load_env()
    
    print("Testing social media API connections...")
    print("-" * 40)
    
    results = []
    results.append(("Meta", test_meta(env)))
    results.append(("X/Twitter", test_x(env)))
    
    print("-" * 40)
    for name, status in results:
        print(f"{name}: {'✓' if status else '✗'}")
    
    return all(status for _, status in results)

if __name__ == '__main__':
    sys.exit(0 if main() else 1)