#!/usr/bin/env python3
"""Post to Instagram via Meta Graph API. Auto-cross-posts to linked Facebook Page."""
import requests
import json
import sys
import os
import time

def load_env(path='{{HERMES_ENV_PATH}}'):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k] = v
    return env

def post_instagram(caption, image_url, env):
    token = env.get('{{META_TOKEN_KEY}}')
    ig_id = '17841454976282357'
    
    if not token:
        print('❌ {{META_TOKEN_KEY}} not found in .env')
        sys.exit(1)
    
    # 1. Create media container
    container_url = f"https://graph.facebook.com/v18.0/{ig_id}/media"
    params = {
        'messaging_product': 'instagram',
        'image_url': image_url,
        'caption': caption,
        'access_token': token
    }
    r = requests.post(container_url, params=params)
    if r.status_code != 200:
        print(f'❌ Container failed: {r.text[:200]}')
        sys.exit(1)
    
    container_id = r.json()['id']
    print(f'✅ Container created: {container_id}')
    
    # 2. Wait for processing (Instagram needs time to process the image)
    print('⏳ Processing image...')
    time.sleep(3)
    
    # 3. Publish container
    publish_url = f"https://graph.facebook.com/v18.0/{ig_id}/media_publish"
    publish_params = {
        'messaging_product': 'instagram',
        'creation_id': container_id,
        'access_token': token
    }
    r2 = requests.post(publish_url, params=publish_params)
    if r2.status_code == 200:
        media_id = r2.json().get('id')
        print(f'✅ Published to Instagram! ID: {media_id}')
        print('✅ Auto-cross-posted to Facebook Page')
        return media_id
    else:
        print(f'❌ Publish failed: {r2.text[:200]}')
        sys.exit(1)

if __name__ == '__main__':
    env = load_env()
    
    # Accept caption and image URL from command line or env vars
    caption = os.environ.get('POST_CAPTION', 'Test post')
    image_url = os.environ.get('POST_IMAGE_URL', '')
    
    if not image_url:
        print('❌ POST_IMAGE_URL required')
        sys.exit(1)
    
    post_instagram(caption, image_url, env)
