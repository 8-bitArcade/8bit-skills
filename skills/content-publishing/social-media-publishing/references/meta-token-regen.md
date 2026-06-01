# Meta API Token Regeneration Guide

## When to Regenerate

- Token expired (check `expires_at` via debug_token endpoint)
- User logged out of Facebook/Meta ("session is invalid because the user logged out")
- Missing permissions (e.g., `pages_manage_posts` not in scopes)
- App settings changed

## Steps

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app (e.g., "8Bit Content Manager")
3. Click **Generate Access Token**
4. Check permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `instagram_manage_insights`
   - `pages_read_engagement`
   - `public_profile`
5. Click **Generate Access Token** → log in → approve
6. Exchange for long-lived token:
   ```
   GET https://graph.facebook.com/v18.0/oauth/access_token
   ?grant_type=fb_exchange_token
   &client_id=APP_ID
   &client_secret=APP_SECRET
   &fb_exchange_token=USER_TOKEN
   ```
7. Update `META_LONG_LIVED_TOKEN` in `~/.hermes/.env`

## Debug Token

Check token validity and scopes:
```
GET https://graph.facebook.com/v18.0/debug_token
?input_token={USER_TOKEN}
&access_token={APP_ID}|{APP_SECRET}
```

## Known Issues

- `pages_manage_posts` permission requires App Review (not available in dev mode)
- Instagram posting works with current token + linked Business Page
- Cross-posting to Facebook Page happens automatically via Instagram Business account