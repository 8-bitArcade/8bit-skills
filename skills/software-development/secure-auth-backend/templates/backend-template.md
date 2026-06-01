# Secure Auth Backend Template

## File Structure
```
backend/
├── package.json
├── server.js          # Express app entry point
├── config.js          # Environment config
├── db.js              # SQLite schema + prepared statements
├── routes/
│   └── auth.js        # WebAuthn endpoints
├── middleware/
│   └── auth.js        # JWT verification
├── utils/
│   └── emailWhitelist.js  # Email validation
└── data/              # SQLite database (auto-created)
```

## Dependencies
```json
{
  "dependencies": {
    "express": "^4.18.2",
    "better-sqlite3": "^9.4.3",
    "@simplewebauthn/server": "^9.0.0",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "express-rate-limit": "^7.1.4",
    "uuid": "^9.0.0"
  }
}
```

## Config (config.js)
```javascript
module.exports = {
  port: process.env.PORT || {{BACKEND_PORT}},
  jwtSecret: process.env.JWT_SECRET || 'change-me',
  jwtRefreshSecret: process.env.JWT_REFRESH_SECRET || 'change-me',
  jwtExpiry: '1h',
  jwtRefreshExpiry: '7d',
  authorizedEmails: (process.env.{{AUTH_EMAILS_KEY}} || 'admin@example.com').split(','),
  rpName: 'App Name',
  rpID: process.env.RP_ID || 'localhost',
  dbPath: process.env.DB_PATH || './data/dataroom.sqlite',
};
```

## Environment Variables
```bash
PORT=3001
JWT_SECRET=<strong-random-string>
JWT_REFRESH_SECRET=<strong-random-string>
{{AUTH_EMAILS_KEY}}=admin@example.com,investor@firm.com
RP_ID=your-domain.com
DB_PATH=./data/app.sqlite
```

## API Endpoints

### Health
`GET /health` — Returns server status

### Auth
`POST /api/auth/check-email` — Validate email against whitelist
`POST /api/auth/register/options` — Start WebAuthn registration
`POST /api/auth/register/complete` — Complete registration
`POST /api/auth/login/options` — Start WebAuthn authentication
`POST /api/auth/login/complete` — Complete authentication
`POST /api/auth/refresh` — Refresh JWT tokens
`GET /api/auth/me` — Get current user info
`POST /api/auth/logout` — Invalidate refresh token

## Security Headers
- Helmet (X-Content-Type-Options, X-Frame-Options, etc.)
- CORS restricted to allowed origins
- Rate limiting (100 req/15min general, 10 auth attempts/15min)
