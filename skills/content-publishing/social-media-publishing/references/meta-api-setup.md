# Meta Developer Portal Setup Notes

## UI Changes (2024+)

- "Products" section renamed to **"Use cases"** in left sidebar
- "Add Product" → **"Add more to this use case"**
- Instagram Graph API found under Use cases, not Products

## Common Errors

### `client_id: "30620018"` (X/Twitter)
- App not linked to project
- Fix: Create project in Developer Portal, link app, regenerate tokens

### `Invalid OAuth access token signature` (Meta)
- Token expired or not exchanged for long-lived version
- Fix: Exchange user token via `fb_exchange_token` grant type

### `No user access token specified` (Meta)
- Using app token (client_credentials) instead of user token
- Fix: Generate user token via Graph API Explorer with proper permissions

### `pages_manage_posts permission required` (Meta)
- Facebook Page posting requires `pages_manage_posts` in addition to `pages_read_engagement`
- Fix: Regenerate token with `pages_manage_posts` checked

### `Only photo or video can be accepted as media type` (Instagram)
- Instagram requires images for posts - text-only not supported
- Fix: Always include `image_url` parameter in media upload

### `Media download has failed` (Instagram)
- The provided `image_url` doesn't meet Instagram requirements
- Fix: Use direct image URLs (not redirects, Wikimedia, or CDN with redirects)
- Host images on your own server or use a reliable image host

### `Unsupported get request. Object with ID '...' does not exist` (Meta)
- Permission issue or incorrect object ID
- Fix: Debug token first, then check object ID validity

## Token Types

| Type | Lifetime | Use Case |
|------|----------|----------|
| App token | ~1 hour | Basic app info, limited permissions |
| User token | ~1 hour | Instagram permissions, page access |
| Long-lived token | 60 days | Production use, exchange user token |

## Instagram Posting Workflow (Container → Publish)

1. Create container: `POST /v18.0/{IG_ACCOUNT_ID}/media`
   - Required params: `messaging_product=instagram`, `image_url`, `caption`
   - Returns: `id` (container ID)

2. Publish container: `POST /v18.0/{IG_ACCOUNT_ID}/media_publish`
   - Required params: `messaging_product=instagram`, `creation_id={container_id}`
   - Returns: `id` (published media ID)

## Facebook Page Posting

- Endpoint: `POST /v18.0/{PAGE_ID}/feed`
- Required params: `message`, `access_token`
- Requires: `pages_manage_posts` permission

## Required Permissions by Platform

### Instagram Posting
- `instagram_basic` (required for all IG operations)
- `instagram_content_publish` (posting)
- `instagram_manage_insights` (analytics)
- `pages_read_engagement` (page access)

### Facebook Page Posting
- `pages_read_engagement` (page access)
- `pages_manage_posts` (posting to pages)

### Combined (Instagram + Facebook)
- `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights`
- `pages_read_engagement`, `pages_manage_posts`
- `public_profile` (user identity)

- **Graph API:** Business accounts, posting, insights, page integration
- **Basic Display:** Personal accounts, read-only mostly
- Use Graph API for content publishing workflows

## Verification Commands

```bash
# Check Meta token validity
curl "https://graph.facebook.com/v18.0/debug_token?input_token=TOKEN&access_token=APP_TOKEN"

# Check X API connection
python3 -c "
from requests_oauthlib import OAuth1
import requests
auth = OAuth1(KEY, client_secret=SECRET, resource_owner_key=TOKEN, resource_owner_secret=TOKEN_SECRET)
r = requests.get('https://api.x.com/2/users/me', auth=auth)
print(f'Status: {r.status_code}')
"

# Test Meta connection (8Bit specific)
python3 -c "
import requests
r = requests.get('https://graph.facebook.com/v18.0/104307015760659',
                 params={'access_token': TOKEN, 'fields': 'name,instagram_business_account{id,username}'})
print(f'Page: {r.json()}')
# IG Account ID: 17841454976282357
# FB Page ID: 104307015760659
"
```