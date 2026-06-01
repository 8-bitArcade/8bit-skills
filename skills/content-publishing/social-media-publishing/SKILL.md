---
name: social-media-publishing
description: Platform-specific API setup, credential management, and posting workflows for automated content distribution across Instagram, Facebook, X/Twitter, YouTube, and TikTok.
category: content-publishing
trigger: social media setup, Instagram API, Facebook API, Meta Graph API, TikTok posting, YouTube publishing, cross-platform content, social credentials
---

# Social Media Publishing Setup & Workflow

Platform-specific API setup, credential management, and posting workflows for automated content distribution.

## Meta (Instagram + Facebook)

### Setup Flow (Meta Developer Portal)

1. Create app at [developer.facebook.com](https://developer.facebook.com) → **My Apps** → **Create App**
2. Select **Business** → name it (e.g., "8Bit Content Manager")
3. **IMPORTANT:** Meta renamed "Products" → **"Use cases"** in the sidebar
4. Click **"Use cases"** → **"Add more to this use case"** → search **"Instagram Graph API"**
5. Select **"API setup with Facebook login"** (NOT Instagram login — needed for Business Page integration)
6. Configure:
   - OAuth redirect URI: `https://localhost/callback`
   - Permissions: `instagram_content_publish`, `instagram_manage_insights`, `pages_read_engagement`
7. Click **Save Changes**

### Token Flow

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app → **Generate Access Token**
3. Check permissions: `pages_read_engagement`, `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights`
4. Click **Generate Access Token** → log in with Facebook → approve
5. **App tokens** (client_credentials) have limited permissions — you need a **user access token** for Instagram
6. Exchange user token for long-lived token:
   ```
   GET https://graph.facebook.com/v18.0/oauth/access_token
   ?grant_type=fb_exchange_token
   &client_id=APP_ID
   &client_secret=APP_SECRET
   &fb_exchange_token=USER_TOKEN
   ```

### Credential Storage

Store in `~/.hermes/.env`:
```
META_FACEBOOK_APP_ID=...
META_FACEBOOK_APP_SECRET=...
M...n### Posting Endpoints

- Instagram: `POST /v18.0/{IG_ACCOUNT_ID}/media` (upload image) → `POST /v18.0/{IG_ACCOUNT_ID}/media_publish`
- Facebook Page: `POST /v18.0/{PAGE_ID}/feed` (text post)
- Ready-made script: `scripts/post-instagram.py` (accepts `POST_CAPTION` + `POST_IMAGE_URL` env vars) — requires `pages_manage_posts` permission
- **Use `~/.hermes/scripts/post-instagram.py` for Instagram posting** (auto-cross-posts to linked Facebook Page)

## X / Twitter

### Setup Requirements

- API v2 requires app attached to a **Project** (created in Developer Portal)
- Tokens generated before project linking **won't work** — must regenerate
- Error `client_id: "30620018"` = app not recognized by project system
- Needs all 4 creds: `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`

### Credential Storage

```
TWITTER_API_KEY=...
T...n### Auth Pattern

Use OAuth 1.0a:
```python
from requests_oauthlib import OAuth1
auth = OAuth1(api_key, client_secret=api_secret,
              resource_owner_key=access_token,
              resource_owner_secret=access_token_secret)
```

## YouTube

### Setup Requirements

- Google Cloud project + YouTube Data API v3 enabled
- OAuth 2.0 credentials (client ID + secret)
- Token storage: refresh token (long-lived) + access token (short-lived)

### Posting Endpoints

- Video upload: `POST /youtube/v3/videos?part=snippet,status`
- Playlist management: `POST /youtube/v3/playlistItems`

## TikTok

### Setup Requirements

- TikTok for Developers account
- Publishing API eligibility: 100+ followers, 3+ posts in 180 days, no violations
- OAuth 2.0 flow

### Posting Endpoints

- Video upload: `POST https://open.tiktokapis.com/v2/post/publish/video/create/`

## Platform Content Strategy

| Platform | Format | Best For |
|----------|--------|----------|
| Instagram | Image/carousel + caption | Visual storytelling, BTS, product shots |
| Facebook | Text + link | Community building, discussion, longer posts |
| X/Twitter | Text (280 char) | Quick thoughts, threads, real-time updates |
| YouTube | Video | Deep dives, tutorials, founder stories |
| TikTok | Short video | Raw authenticity, building-in-public |

## Pitfalls

- **Meta UI changes:** "Products" → "Use cases" (2024+). Always check current sidebar labels.
- **Token expiration:** User tokens expire in ~1 hour. Exchange for long-lived (60 days) immediately.
- **Project linking (X):** App must be linked to project BEFORE generating tokens. Old tokens don't work after linking.
- **Instagram login vs Facebook login:** Use Facebook login for Business Page integration. Instagram login is for personal accounts only.
- **App tokens vs User tokens:** App tokens (client_credentials) can't access Instagram permissions. Need user token flow.
- **Instagram must be linked to Facebook Page FIRST:** Before Instagram appears in API responses, link IG to your FB Page via Page Settings → Linked Accounts → Instagram → Connect. Without this, `instagram_business_account` returns null.
- **Token exchange can fail with "could not be decrypted":** If long-lived token fails, use the original user token directly. The exchange endpoint sometimes returns unusable tokens in Development Mode.
- **Token debug endpoint:** Use `GET /debug_token?input_token={TOKEN}&access_token={APP_TOKEN}` to check token validity, scopes, and expiration. Requires app token (`APP_ID|APP_SECRET`), NOT user token.
- **Facebook Page posting requires `pages_manage_posts` permission:** `pages_read_engagement` alone is insufficient for posting to Pages. You need BOTH `pages_read_engagement` AND `pages_manage_posts` for Page posting workflows.
- **Instagram posts require images:** Text-only posts are rejected with "Only photo or video can be accepted as media type." Always provide `image_url` parameter for Instagram media uploads.
- **Long-lived token preserves original scopes:** When exchanging user token for long-lived version, the new token inherits ALL scopes from the original. If original token missing permissions, exchange won't add them — regenerate the user token first.
- **Instagram media download failures:** If `image_url` returns "Media download has failed", the URL doesn't meet Instagram requirements. Use direct image URLs (not redirects or Wikimedia). Host images on your own server or use a reliable CDN.
- **Instagram auto-cross-posting does NOT work for API posts:** The "Automatic Posting" toggle in Instagram app settings only applies to posts made via the Instagram app itself. Posts created via the Graph API (`/media` endpoint) will NOT auto-cross-post to the linked Facebook Page. To post to both IG and FB, you need `pages_manage_posts` permission for direct FB posting OR post manually in the IG app.
- **Instagram posts cannot be deleted via API:** `DELETE /v18.0/{media_id}` returns 400 "An unknown error occurred". Test posts must be deleted manually in the Instagram app.
- **`pages_manage_posts` requires App Review even in Development Mode:** This permission is not available in dev mode for most apps. You must submit it for App Review with a screen recording demo. Until approved, Facebook Page posting is blocked.
- **Long-lived tokens can be revoked by user logout:** If a user logs out of Facebook, previously exchanged long-lived tokens become invalid ("Error validating access token: The session is invalid because the user logged out"). Regenerate from Graph API Explorer and re-exchange.
- **Token exchange can fail silently:** The `/oauth/access_token` exchange endpoint sometimes returns tokens that are unusable in Development Mode. Test the exchanged token immediately with a simple API call.
- **Instagram API posts do NOT auto-cross-post to Facebook:** The "Automatic Posting" toggle in Instagram settings only works for posts made through the Instagram app itself. API posts bypass the cross-posting system entirely. To post to both platforms, you need `pages_manage_posts` permission for Facebook API posting.
- **`pages_manage_posts` permission may not appear in Graph API Explorer:** This permission is restricted to "Business" category apps or requires App Review submission. If it doesn't show, try: (1) Add yourself as Developer in App Settings → Roles, (2) Set app category to "Business" or "Marketing", (3) Submit for App Review with screen recording demo.
- **Facebook Page posting requires BOTH permissions:** You need `pages_read_engagement` AND `pages_manage_posts` with a Page Token (not User Token). Get Page Token via: `GET /v18.0/{PAGE_ID}?fields=access_token&access_token={USER_TOKEN}`.
- **Instagram container status checking:** Media container status endpoint only supports `id`, `status_code`, and `media_type` fields. `error` field does NOT exist on containers — use `status_code` to check if container is `FINISHED` before publishing.
- **Token revocation:** Long-lived tokens can be revoked if the user logs out of Facebook or changes password. If you get "Invalid OAuth 2.0 Access Token" or "session is invalid", regenerate the token via Graph API Explorer.
- **Working Instagram posting script:** `~/.hermes/scripts/post-instagram.py` — accepts `POST_CAPTION` and `POST_IMAGE_URL` env vars. Tested and functional.
- **Token revocation on logout:** If you log out of Facebook/Meta, long-lived tokens tied to that session become invalid ("session is invalid because the user logged out"). Regenerate the user token via Graph API Explorer and re-exchange for long-lived.
- **Working posting script:** `~/.hermes/scripts/post-instagram.py` handles Instagram posting with auto-cross-post to linked Facebook Page. Set `POST_CAPTION` and `POST_IMAGE_URL` env vars, run with `python3`.

## Troubleshooting Meta Tokens

1. Debug token: `GET https://graph.facebook.com/v18.0/debug_token?input_token={USER_TOKEN}&access_token={APP_ID}|{APP_SECRET}`
2. Check scopes include: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`
3. Check expiration: `expires_at` timestamp
4. If scopes missing: regenerate token with correct permissions checked
5. If token invalid: regenerate from Graph API Explorer
6. If Instagram not showing: link IG to FB Page first (see Pitfalls above)
7. If long-lived token fails with "session is invalid because the user logged out": The user's Facebook session was terminated. Regenerate a fresh User Token from Graph API Explorer and re-exchange for long-lived.
8. If `pages_manage_posts` not available in token generator: This permission requires App Review. Go to App → App Review → request permission with screen recording demo.

## Current Meta Setup Status (as of May 2026)

- **Instagram posting:** ✅ Works via Graph API (`~/.hermes/scripts/post-instagram.py`)
- **Facebook Page posting:** ❌ Blocked — requires `pages_manage_posts` via App Review (pending)
- **Auto-cross-posting:** ❌ Only works for in-app IG posts, not API posts
- **App:** "8Bit Content Manager" (ID: 996540993337274)
- **Token:** Long-lived in `~/.hermes/.env` (60-day expiry, can be revoked by logout)
7. See `references/meta-token-regen.md` for full token regeneration steps

## Verification

Test Meta connection:
```python
import requests
r = requests.get('https://graph.facebook.com/v18.0/me/accounts',
                 params={'access_token': TOKEN, 'fields': 'id,name,instagram_business_account'})
# Should return your Pages + linked IG accounts
```

Test X connection:
```python
from requests_oauthlib import OAuth1
auth = OAuth1(KEY, client_secret=SECRET, resource_owner_key=TOKEN, resource_owner_secret=TOKEN_SECRET)
r = requests.get('https://api.x.com/2/users/me', auth=auth)
# Should return 200 with user data
```